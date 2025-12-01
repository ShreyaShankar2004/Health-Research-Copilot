import os, json, argparse, requests
from tqdm import tqdm

BASE = "https://clinicaltrials.gov/api/v2/studies"

def fetch_trials(query: str, max_records: int = 50):
    # Simple paged fetch
    page_size = 25
    for start in range(0, max_records, page_size):
        params = {"q": query, "countTotal": "true", "pageSize": page_size, "pageToken": str(start)}
        r = requests.get(BASE, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        studies = data.get("studies", [])
        for s in studies:
            ident = s.get("protocolSection", {}).get("identificationModule", {})
            id_ = ident.get("nctId", "NCT-NA")
            title = ident.get("briefTitle", "")
            desc = s.get("protocolSection", {}).get("descriptionModule", {}).get("briefSummary", "")
            if desc:
                yield {
                    "source": "clinicaltrials",
                    "id": id_,
                    "title": title,
                    "url": f"https://clinicaltrials.gov/study/{id_}",
                    "text": desc
                }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--max_records", type=int, default=50)
    ap.add_argument("--outdir", default="data/corpora")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    out = os.path.join(args.outdir, f"ct_{args.query.replace(' ', '_')}.jsonl")

    cnt = 0
    with open(out, "w", encoding="utf-8") as f:
        for rec in tqdm(fetch_trials(args.query, args.max_records), desc="ClinicalTrials.gov"):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cnt += 1
    print(f"Saved {cnt} records -> {out}")
