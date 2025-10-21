# Smart Resume Screener (Full)
This project provides a FastAPI backend that:
- accepts resume uploads (text for demo),
- extracts sections (summary, skills, experience, education),
- computes embeddings (OpenAI if OPENAI_API_KEY set, otherwise deterministic dummy),
- indexes section embeddings in FAISS,
- ranks candidates for a job description.

## Run locally
1. Create and activate a Python environment
2. Install dependencies:
   pip install -r requirements.txt
3. (optional) Set OPENAI_API_KEY if you want OpenAI embeddings
   export OPENAI_API_KEY="sk-..."
4. Start:
   uvicorn main:app --reload --port 8000
5. Upload a resume:
   curl -X POST "http://127.0.0.1:8000/upload" -F "files=@/path/to/resume.txt"
6. Rank:
   curl -X POST "http://127.0.0.1:8000/rank" -H "Content-Type: application/json" -d '{"title":"Data Scientist","description":"python machine learning"}'
