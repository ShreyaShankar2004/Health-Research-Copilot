
import sys
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from src.config import EMBEDDING_MODEL

def test_query(q: str, index_dir: str = "models/faiss", k: int = 5):
    idx_path = Path(index_dir) / "index.faiss"
    meta_path = Path(index_dir) / "meta.npy"
    if not idx_path.exists() or not meta_path.exists():
        print("Index or meta not found in", index_dir)
        return
    index = faiss.read_index(str(idx_path))
    meta = np.load(str(meta_path), allow_pickle=True).tolist()
    model = SentenceTransformer(EMBEDDING_MODEL)
    qvec = model.encode([q], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    D, I = index.search(qvec, k)
    for rank, idx in enumerate(I[0]):
        if idx < 0 or idx >= len(meta):
            continue
        m = meta[idx]
        print(f"[{rank+1}] score={float(D[0][rank]):.4f} title={m.get('title')[:100]} source={m.get('source')}")
        print("  url:", m.get("url"))
        print("  snippet:", m.get("text")[:300].replace("\n"," "), "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/test_faiss_query.py \"your query\"")
        sys.exit(1)
    test_query(sys.argv[1])
