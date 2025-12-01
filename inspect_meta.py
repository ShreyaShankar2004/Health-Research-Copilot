# tools/inspect_meta.py
import numpy as np

meta = np.load("models/faiss/meta.npy", allow_pickle=True).tolist()

print(f"Total docs: {len(meta)}")
for i, m in enumerate(meta[:10]):  # show first 10 docs
    print(f"\nDoc {i+1}:")
    print("Title:", m.get("title", ""))
    print("Text:", m.get("text", "")[:200])
