import os, json, time, argparse
from Bio import Entrez
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
Entrez.email = os.getenv("ENTREZ_EMAIL", "shankarshreya944@gmail.com")

def fetch_pubmed(query: str, retmax: int = 50):
    search = Entrez.esearch(db="pubmed", term=query, retmax=retmax, sort="relevance")
    res = Entrez.read(search)
    ids = res.get("IdList", [])
    for pmid in tqdm(ids, desc="PubMed efetch"):
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
        text = handle.read().strip()
        if text:
            yield {"source": "pubmed", "id": pmid, "title": "", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", "text": text}
        time.sleep(0.34)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--retmax", type=int, default=50)
    ap.add_argument("--outdir", default="data/corpora")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    out = os.path.join(args.outdir, f"pubmed_{args.query.replace(' ', '_')}.jsonl")

    cnt = 0
    with open(out, "w", encoding="utf-8") as f:
        for rec in fetch_pubmed(args.query, args.retmax):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cnt += 1
    print(f"Saved {cnt} records -> {out}")
