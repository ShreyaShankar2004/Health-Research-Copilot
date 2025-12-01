# app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

from src.config import groq_client
from src.rag.qa import RagEngine
from src.agents.safety import safety_filter
from src.agents.planner import Planner

# ---------------------------
# FastAPI Setup
# ---------------------------
app = FastAPI(title="Personal Health Research Copilot", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# ---------------------------
# Init RAG + Planner
# ---------------------------
rag = RagEngine(index_dir="models/faiss")
planner = Planner()

# ---------------------------
# External Source Queries
# ---------------------------
def query_arxiv(q: str):
    url = f"http://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results=2"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{"title": f"Arxiv: {q}", "snippet": r.text[:300], "source": "ARXIV"}]
    except:
        return []
    return []

def query_wikipedia(q: str):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{q}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return [{
                "title": data.get("title", "Wikipedia"),
                "snippet": data.get("extract", ""),
                "source": "WIKIPEDIA"
            }]
    except:
        return []
    return []

def query_europepmc(q: str):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&pageSize=2"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json().get("resultList", {}).get("result", [])
            return [{
                "title": item.get("title", "EuropePMC"),
                "snippet": item.get("abstractText", "")[:400],
                "source": "EUROPE PMC"
            } for item in data]
    except:
        return []
    return []

def query_clinicaltrials(q: str):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={q}&min_rnk=1&max_rnk=2&fmt=json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            studies = r.json()["FullStudiesResponse"]["FullStudies"]
            return [{
                "title": study["Study"]["ProtocolSection"]["IdentificationModule"]["OfficialTitle"],
                "snippet": study["Study"]["ProtocolSection"]["DescriptionModule"].get("BriefSummary", ""),
                "source": "CLINICALTRIALS.GOV"
            } for study in studies]
    except:
        return []
    return []

def query_semantic_scholar(q: str):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=2&fields=title,abstract,authors,year"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            return [{
                "title": item.get("title", "Semantic Scholar"),
                "snippet": item.get("abstract", "")[:400],
                "source": "SEMANTIC SCHOLAR"
            } for item in data]
    except:
        return []
    return []

# ---------------------------
# Endpoints
# ---------------------------
@app.get("/")
def root():
    return {"message": "🚀 Health Copilot is running with Multi-Source Search!"}

@app.get("/search")
def search(q: str = Query(...), k: int = 5):
    q = safety_filter(q)
    hits = rag.retrieve(q, k=k)
    return {"results": hits}

@app.get("/fallback")
def fallback_search(q: str = Query(...)):
    q = safety_filter(q)
    results = []

    # --- Europe PMC (PubMed + bioRxiv + medRxiv)
    try:
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&pageSize=3"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            papers = r.json().get("resultList", {}).get("result", [])
            for p in papers:
                title = p.get("title", "No Title")
                snippet = p.get("abstractText", "")
                if snippet:
                    snippet = snippet[:500] + "..." if len(snippet) > 500 else snippet
                    

                # EuropePMC returns a "source" field → can be "MED" (PubMed) or "PMC"
                raw_source = p.get("source", "").upper()
                pmid = p.get("id", "")

                if raw_source == "MED":   # PubMed
                    source = "PUBMED"
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                elif raw_source == "PMC":  # PubMed Central
                    source = "PUBMED CENTRAL"
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmid}/"
                else:  # fallback (bioRxiv, EuropePMC internal, etc.)
                    source = "EUROPE PMC"
                    url = f"https://europepmc.org/article/{raw_source}/{pmid}"


                results.append({
                    "title": title,
                    "text": snippet,
                    "url": url,
                    "source": source
                })
 

    except Exception as e:
        print("EuropePMC error:", e)

    # --- Arxiv
    try:
        arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results=2"
        r = requests.get(arxiv_url, timeout=10)
        if r.status_code == 200:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(r.content)
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title = entry.find("{http://www.w3.org/2005/Atom}title").text
                summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
                results.append({
                    "title": title.strip(),
                    "text": summary.strip()[:500] + "...",
                    "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
                    "source": "ARXIV"
                })
    except Exception as e:
        print("Arxiv error:", e)

    # --- ClinicalTrials.gov
    try:
        url = f"https://clinicaltrials.gov/api/query/full_studies?expr={q}&min_rnk=1&max_rnk=2&fmt=json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            studies = r.json()["FullStudiesResponse"]["FullStudies"]
            for s in studies:
                title = s["Study"]["ProtocolSection"]["IdentificationModule"]["OfficialTitle"]
                desc = s["Study"]["ProtocolSection"]["DescriptionModule"].get("BriefSummary", "")
                results.append({
                    "title": title,
                    "text": desc[:500] + "...",
                    "url": "https://clinicaltrials.gov/study/" + s["Study"]["ProtocolSection"]["IdentificationModule"]["NCTId"],
                    "source": "CLINICALTRIALS.GOV"
                })
    except Exception as e:
        print("ClinicalTrials error:", e)

    # --- Semantic Scholar
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=2&fields=title,abstract,url"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            for item in data:
                results.append({
                    "title": item.get("title", "No Title"),
                    "text": (item.get("abstract", "") or "")[:500] + "...",
                    "url": item.get("url", ""),
                    "source": "SEMANTIC SCHOLAR"
                })
    except Exception as e:
        print("Semantic Scholar error:", e)

    # --- Wikipedia
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{q}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results.append({
                "title": data.get("title", ""),
                "text": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "source": "WIKIPEDIA"
            })
    except Exception as e:
        print("Wikipedia error:", e)

    return {"results": results}
