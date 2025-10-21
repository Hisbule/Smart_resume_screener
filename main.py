import os
import uuid
import logging
import numpy as np
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from parser import extract_text_from_file, split_sections
from embeddings import get_embed_service
from indexer import init_global
from models import init_db, SessionLocal, Candidate

app = FastAPI(title="Smart Resume Screener - Full")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart-resume")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (replace the lines above with this)

# Define a persistent data directory, configurable via environment variable
# Defaults to "." (current directory) if not set
DATA_DIR = os.getenv("DATA_DIR", ".")
# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True) 

init_db() # init_db is defined in models.py
embed_svc = get_embed_service()
DIM = embed_svc.dim
# Use the new DATA_DIR for the index path
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index") 
idx = init_global(DIM, INDEX_PATH)

# ... (rest of the file is unchanged)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _to_vector(enc):
    arr = np.asarray(enc)
    if arr.size == 0:
        raise ValueError("empty embedding returned")
    if arr.ndim == 1:
        return arr.astype("float32")
    return arr.reshape(-1)[0:idx.dim].astype("float32")

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    results = []
    for file in files:
        data = await file.read()
        text = extract_text_from_file(file.filename, data)
        sections = split_sections(text) or {}
        cid = str(uuid.uuid4())

        embeddings = {}
        vectors = []
        ids = []
        # This loop correctly skips the 'contacts' dict saved by the new parser
        for sec in ["skills", "experience", "summary", "education"]:
            txt = (sections.get(sec) or "").strip()
            if not txt:
                continue
            enc = embed_svc.encode(txt)
            vec = _to_vector(enc)
            embeddings[sec] = vec.tolist()
            vectors.append(vec)
            ids.append(f"{cid}::{sec}")

        cand = Candidate(id=cid, filename=file.filename, sections=sections, embeddings=embeddings)
        try:
            db.add(cand)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.exception("DB save error for %s: %s", cid, e)
            raise HTTPException(status_code=500, detail="Failed to save candidate")

        if vectors:
            mat = np.stack(vectors, axis=0)
            try:
                idx.add(mat, ids)
                logger.info("Added %d vectors for candidate %s to FAISS (ntotal=%d)", len(ids), cid, idx.ntotal)
            except Exception as e:
                logger.exception("FAISS add error for %s: %s", cid, e)

        results.append({"candidate_id": cid, "filename": file.filename, "status": "uploaded"})
    return {"uploaded": results}

class JD(BaseModel):
    title: str
    description: str

@app.post("/rank")
async def rank(jd: JD, db: Session = Depends(get_db)):
    try:
        q_enc = embed_svc.encode(jd.description)
        q_vec = _to_vector(q_enc).reshape(1, -1)
    except Exception as e:
        logger.exception("Embedding error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create query embedding")

    topk = 50
    try:
        results = idx.search(q_vec, top_k=topk)[0]
    except Exception as e:
        logger.exception("FAISS search failed: %s", e)
        raise HTTPException(status_code=500, detail="Search failed")

    agg = {}
    for ident, score in results:
        if "::" in ident:
            cid, sec = ident.split("::", 1)
        else:
            cid, sec = ident, "all"
        agg.setdefault(cid, 0.0)
        agg[cid] = max(agg[cid], score)

    out = []
    
    
    
    for cid, sc in sorted(agg.items(), key=lambda x: -x[1])[:20]:
        cand = db.query(Candidate).filter(Candidate.id == cid).first()
        if not cand:
            continue
        
        sections = cand.sections or {}
        contacts = sections.get("contacts", {}) # Get the contacts dict
        
        edu_raw = sections.get("education", "")
        skills_raw = sections.get("skills", "")
        exp_raw = sections.get("experience", "")
        summary_short = (sections.get("summary", "")[:250]).strip()

        # Build the new output structure
        output_item = {
            "candidate_id": cid,
            "filename": cand.filename,
            "score": float(sc),
            "name": contacts.get("name", ""),
            "phone": contacts.get("phone", ""),
            "email": contacts.get("email", ""),
            "links": contacts.get("links", ""),
            "summary": summary_short,
            "education": edu_raw,
            "skills": skills_raw,
            "experience": exp_raw
        }
        
        out.append(output_item)
    
    return {"results": out}


@app.get("/candidate/{cid}")
async def get_candidate(cid: str, db: Session = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == cid).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"id": cand.id, "filename": cand.filename, "sections": cand.sections}

@app.get("/debug/index")
async def debug_index():
    return {"ntotal": idx.ntotal, "id_map_len": len(idx.id_map), "dim": idx.dim}

@app.get("/debug/list_candidates")
async def debug_list_candidates(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.execute("SELECT id, filename FROM candidates LIMIT :limit", {"limit": limit}).fetchall()
    return [{"id": r[0], "filename": r[1]} for r in rows]