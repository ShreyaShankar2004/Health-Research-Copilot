# src/rag/retrievers.py

import os
import numpy as np
from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer

from langchain_community.document_loaders import ArxivLoader, WikipediaLoader
from langchain_community.utilities import PubMedAPIWrapper

from src.config import EMBEDDING_MODEL


def format_results(docs, source: str) -> List[Dict]:
    """Convert raw documents into a clean list of dicts."""
    results = []
    for doc in docs:
        results.append({
            "title": getattr(doc, "metadata", {}).get("title", None) or getattr(doc, "page_content", "")[:50],
            "text": doc.page_content if hasattr(doc, "page_content") else str(doc),
            "url": getattr(doc, "metadata", {}).get("source", ""),
            "source": source
        })
    return results


# -----------------------------
# PubMed / Arxiv / Wiki
# -----------------------------
def get_pubmed_results(query: str, k: int = 3) -> List[Dict]:
    try:
        pubmed = PubMedAPIWrapper()
        docs = pubmed.run(query)
        if isinstance(docs, str):
            docs = [docs]
        return format_results(docs, "pubmed")
    except Exception as e:
        print(f"[Retriever:PubMed] Error: {e}")
        return []


def get_arxiv_results(query: str, k: int = 3) -> List[Dict]:
    try:
        loader = ArxivLoader(query=query, max_results=k)
        docs = loader.load()
        return format_results(docs, "arxiv")
    except Exception as e:
        print(f"[Retriever:Arxiv] Error: {e}")
        return []


def get_wikipedia_results(query: str, k: int = 3) -> List[Dict]:
    try:
        loader = WikipediaLoader(query=query, load_max_docs=k)
        docs = loader.load()
        return format_results(docs, "wikipedia")
    except Exception as e:
        print(f"[Retriever:Wikipedia] Error: {e}")
        return []


def get_all_results(query: str) -> List[Dict]:
    results = []
    results.extend(get_pubmed_results(query))
    results.extend(get_arxiv_results(query))
    results.extend(get_wikipedia_results(query))
    return results


# -----------------------------
# FAISS Keyword + Semantic Search
# -----------------------------
def get_faiss_results(query: str, k: int = 5) -> List[Dict]:
    """
    Search FAISS and only return results that actually contain the keyword
    in title or text (case-insensitive, partial match).
    """
    index_dir = "models/faiss"
    model = SentenceTransformer(EMBEDDING_MODEL)

    index = faiss.read_index(os.path.join(index_dir, "index.faiss"))
    meta = np.load(os.path.join(index_dir, "meta.npy"), allow_pickle=True).tolist()

    qvec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    D, I = index.search(qvec, k)

    query_lower = query.lower()
    hits = []

    for rank, idx in enumerate(I[0]):
        m = dict(meta[idx])
        text = m.get("text", "")
        title = m.get("title", "")

        combined = f"{title} {text}".lower()

        # ✅ Case-insensitive + substring match
        if query_lower in combined:
            hits.append({
                "rank": rank + 1,
                "score": float(D[0][rank]),
                "title": title,
                "url": m.get("url", ""),
                "source": m.get("source", "faiss"),
                "orig_id": m.get("orig_id", ""),
                "text": text[:1500]
            })

    return hits
