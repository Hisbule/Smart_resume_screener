import faiss
import numpy as np
import os
import pickle
from typing import List

class FaissIndex:
    def __init__(self, dim: int, path: str = None):
        if dim is None or dim <= 0:
            raise ValueError("dim must be > 0")
        self.dim = int(dim)
        self.path = path
        self.index = faiss.IndexFlatIP(self.dim)
        self.id_map: List[str] = []

        if self.path:
            idx_path = self.path + ".idx"
            ids_path = self.path + ".ids"
            if os.path.exists(idx_path) and os.path.exists(ids_path):
                try:
                    self.index = faiss.read_index(idx_path)
                    with open(ids_path, "rb") as f:
                        self.id_map = pickle.load(f)
                except Exception as e:
                    print("Failed to load existing FAISS index:", e)

    def add(self, vectors: np.ndarray, ids: List[str]):
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if vectors.shape[1] != self.dim:
            raise ValueError(f"vector dim {vectors.shape[1]} != index dim {self.dim}")
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.id_map.extend(ids)
        self.save()

    def search(self, q: np.ndarray, top_k: int = 10):
        q = np.asarray(q, dtype=np.float32)
        if q.ndim == 1:
            q = q.reshape(1, -1)
        if q.shape[1] != self.dim:
            raise ValueError(f"query dim {q.shape[1]} != index dim {self.dim}")
        faiss.normalize_L2(q)
        D, I = self.index.search(q, top_k)
        results = []
        for row_ids, row_scores in zip(I, D):
            res = []
            for idx, score in zip(row_ids, row_scores):
                if idx == -1:
                    continue
                res.append((self.id_map[idx], float(score)))
            results.append(res)
        return results

    def save(self):
        if not self.path:
            return
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        faiss.write_index(self.index, self.path + ".idx")
        with open(self.path + ".ids", "wb") as f:
            pickle.dump(self.id_map, f)

    @property
    def ntotal(self):
        return int(self.index.ntotal)

_GLOBAL = None
def init_global(dim: int, path: str = None):
    global _GLOBAL
    if _GLOBAL is None:
        _GLOBAL = FaissIndex(dim, path)
    return _GLOBAL
