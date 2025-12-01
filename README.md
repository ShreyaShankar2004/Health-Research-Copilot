# Health-Research-Copilot
AI-Powered Multi-Source Medical Literature Explorer (RAG + Agentic Workflow + NLP Summarization)

 Overview

Health Research Copilot is an advanced AI-driven tool designed to help researchers, students, and clinicians explore medical literature across multiple global sources such as PubMed/EuropePMC, ArXiv, Semantic Scholar, ClinicalTrials.gov, Wikipedia, and optional integrations like SpringerLink, Elsevier, IEEE Xplore.

It uses:

RAG (Retrieval-Augmented Generation)

Agentic AI Planners

NLP summarization & ranking

PDF ingestion/extraction

A React-based UI + FastAPI backend

Bookmarking & user accounts (optional)

This project simulates how a modern health research assistant (like a mini Google Scholar + AI Copilot) would work.

 Key Features
 1. Multi-Source Research Search

Fetches papers from:

EuropePMC (PubMed + BioRxiv + MedRxiv)

ArXiv

Semantic Scholar

ClinicalTrials.gov

Wikipedia

(Optional) SpringerLink, IEEE Xplore, Elsevier Scopus APIs

 2. RAG-Based Question Answering

Ask natural-language questions:

“How does long COVID affect heart function?”
“Compare Paxlovid vs Molnupiravir effectiveness.”


The backend retrieves relevant papers → passes them to a Groq-powered LLM → returns a consolidated medical answer with citations.

 3. Agentic AI Planner

Your system includes:

A Planner Agent → decides which tools to use

A Search Agent → fetches data

A Summarizer Agent → condenses long abstracts

A Safety Agent → prevents medical misinformation

 4. NLP Summarization & Ranking

Automatic:

Sentence-level summarization

Relevance scoring

Highlight extraction

Research ranking

<img width="1915" height="965" alt="image" src="https://github.com/user-attachments/assets/55c0e037-a098-4dcd-a40a-fb7117041bf3" />

<img width="1919" height="961" alt="image" src="https://github.com/user-attachments/assets/61ad53f6-ad9f-40d8-bc92-1d238c9fb3d5" />

Redirected:

<img width="1919" height="964" alt="image" src="https://github.com/user-attachments/assets/70f50d88-4e69-4120-a0d3-2757373ad967" />


