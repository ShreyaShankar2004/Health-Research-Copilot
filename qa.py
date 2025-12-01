import os, numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
from src.config import groq_client, EMBEDDING_MODEL
from src.utils.postprocess import add_disclaimer

class RagEngine:
    def __init__(self, index_dir="models/faiss"):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = faiss.read_index(os.path.join(index_dir, "index.faiss"))
        self.meta = np.load(os.path.join(index_dir, "meta.npy"), allow_pickle=True).tolist()

    def retrieve(self, question: str, k: int = 5) -> List[Dict]:
        qvec = self.model.encode([question], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(qvec, k)
        hits = []
        for rank, idx in enumerate(I[0]):
            m = dict(self.meta[idx])
            hits.append({
                "rank": rank + 1,
                "score": float(D[0][rank]),
                "title": m.get("title",""),
                "url": m.get("url",""),
                "source": m.get("source",""),
                "orig_id": m.get("orig_id",""),
                "text": m.get("text","")[:1500]
            })
        return hits

    def answer(self, question: str, k: int = 5) -> Dict:
        docs = self.retrieve(question, k=k)
        context = "\n\n".join([f"[{d['rank']}] {d['source'].upper()} {d['orig_id']} — {d['text']}" for d in docs])

        system = (
            "You are a clinical research assistant. "
            "Answer strictly using the CONTEXT. Cite sources with bracket numbers [1], [2], etc. "
            "If not answerable from context, say you don't know."
        )
        user = f"QUESTION:\n{question}\n\nCONTEXT:\n{context}\n\nReturn a concise, evidence-grounded answer with citations."

        resp = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0.2
        )
        answer = resp.choices[0].message["content"]


        conf = sum([d["score"] for d in docs[:3]]) / max(1, min(3, len(docs)))
        return {
            "answer": add_disclaimer(answer),
            "citations": [{"rank": d["rank"], "source": d["source"], "id": d["orig_id"], "url": d["url"]} for d in docs],
            "confidence": round(conf, 3)
        }
