from sentence_transformers import SentenceTransformer
import numpy as np

class EmbedService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        emb = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return emb.astype(np.float32)

# Singleton
_svc = None

def get_embed_service():
    global _svc
    if _svc is None:
        _svc = EmbedService(model_name="all-MiniLM-L6-v2")  # or "BAAI/bge-base-en-v1.5"
    return _svc
