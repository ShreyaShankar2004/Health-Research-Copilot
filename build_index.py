import os
import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

# Try to use your project's EMBEDDING_MODEL from src.config
try:
    from src.config import EMBEDDING_MODEL
except Exception:
    # fallback if config not present
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Paths (adapt if your structure is different)
ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "corpora"
OUT_DIR = ROOT / "models" / "faiss"

# chunking utility: try to use your project util, otherwise fallback
try:
    from src.utils.textsplit import chunk_text_words
except Exception:
    def chunk_text_words(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Simple fallback: sliding window split on whitespace."""
        words = text.split()
        if len(words) == 0:
            return []
        chunks = []
        i = 0
        while i < len(words):
            chunk = words[i : i + chunk_size]
            chunks.append(" ".join(chunk))
            i += chunk_size - overlap
        return chunks

def load_corpus_from_json_and_csv(data_dir: Path) -> List[Dict]:
    docs = []
    # JSON files: expect list of dicts OR one doc per file
    for p in sorted(data_dir.glob("*.json")):
        try:
            raw = json.loads(p.read_text(encoding="utf8"))
            if isinstance(raw, list):
                for item in raw:
                    docs.append(normalize_doc(item))
            elif isinstance(raw, dict):
                docs.append(normalize_doc(raw))
        except Exception as e:
            print(f"[load] failed to read {p}: {e}")

    # CSV optional: try pandas if available
    for p in sorted(data_dir.glob("*.csv")):
        try:
            import pandas as pd
            df = pd.read_csv(p)
            for _, row in df.iterrows():
                item = row.to_dict()
                docs.append(normalize_doc(item))
        except Exception as e:
            print(f"[load] failed to read csv {p}: {e}")

    return docs

def normalize_doc(item: Dict) -> Dict:
    """
    Normalize a raw doc dict into {title, text, url, source}
    Accepts many common key names (abstract, content, body, title...)
    """
    t = item.get("title") or item.get("name") or ""
    text = item.get("text") or item.get("abstract") or item.get("content") or item.get("body") or t
    url = item.get("url") or item.get("link") or ""
    source = item.get("source") or item.get("collection") or "pubmed"
    return {"title": t, "text": str(text), "url": url, "source": source}

def build_index(documents: List[Dict], model_name: str = EMBEDDING_MODEL,
                chunk_size:int=400, overlap:int=50, batch_size:int=32):
    """
    1) Chunk docs into pieces
    2) Embed chunks with SentenceTransformer (normalize_embeddings=True)
    3) Build FAISS IndexFlatIP (inner product on normalized vectors = cosine)
    4) Save index and meta aligned with vectors
    """
    if len(documents) == 0:
        print("No documents found in data/corpora — put your JSON/CSV files there and try again.")
        return

    model = SentenceTransformer(model_name)
    print("Using embedding model:", model_name)

    texts = []
    meta = []
    for doc_idx, doc in enumerate(documents):
        t = doc.get("text", "")
        if not t or len(t.strip()) == 0:
            continue
        chunks = chunk_text_words(t, chunk_size=chunk_size, overlap=overlap)
        if len(chunks) == 0:
            chunks = [t[:chunk_size]]
        for i, c in enumerate(chunks):
            texts.append(c)
            # attach doc-level metadata + chunk id
            meta.append({
                "title": doc.get("title",""),
                "url": doc.get("url",""),
                "source": doc.get("source",""),
                "orig_doc_index": doc_idx,
                "chunk_id": i,
                "text": c  # store the chunk text for display
            })

    if len(texts) == 0:
        print("No text chunks created (documents may be empty).")
        return

    print(f"Total chunks to embed: {len(texts)}")

    # embed in batches; ensure outputs are numpy arrays and normalized
    all_embeds = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
        batch_texts = texts[i:i+batch_size]
        embs = model.encode(batch_texts, convert_to_numpy=True, normalize_embeddings=True)
        all_embeds.append(embs)
    embeddings = np.vstack(all_embeds).astype("float32")
    dim = embeddings.shape[1]
    print("Embeddings shape:", embeddings.shape)

    # Build FAISS index: IndexFlatIP works with normalized vectors for cosine similarity
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print("FAISS index size (n vectors):", index.ntotal)

    # Save
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx_path = OUT_DIR / "index.faiss"
    meta_path = OUT_DIR / "meta.npy"
    faiss.write_index(index, str(idx_path))
    np.save(str(meta_path), np.array(meta, dtype=object))
    print("Saved index ->", idx_path)
    print("Saved meta ->", meta_path)

def main():
    print("Loading raw docs from", DATA_DIR)
    docs = load_corpus_from_json_and_csv(DATA_DIR)
    print("Raw documents loaded:", len(docs))
    build_index(docs)

if __name__ == "__main__":
    main()
