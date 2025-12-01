import os, json, argparse, feedparser
from tqdm import tqdm

def fetch_who(feed_url: str, max_items: int = 50):
    d = feedparser.parse(feed_url)
    for entry in d.entries[:max_items]:
        text = f"{entry.get('title','')}\n\n{entry.get('summary','')}"
        yield {
            "source": "who",
            "id": entry.get("id", entry.get("link", "")),
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "text": text
        }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default="https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml")
    ap.add_argument("--max_items", type=int, default=50)
    ap.add_argument("--outdir", default="data/corpora")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    out = os.path.join(args.outdir, f"who_feed.jsonl")

    with open(out, "w", encoding="utf-8") as f:
        cnt = 0
        for rec in fetch_who(args.feed, args.max_items):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cnt += 1
    print(f"Saved {cnt} records -> {out}")
