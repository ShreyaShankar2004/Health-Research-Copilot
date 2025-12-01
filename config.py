import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing in .env")

ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL", "shankarshreya944@gmail.com")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

groq_client = Groq(api_key=GROQ_API_KEY)
