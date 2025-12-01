# src/agents/planner.py

from typing import Dict, List
from src.rag import retrievers


class Planner:
    """
    Planner decides which retriever(s) to use based on the query.
    """

    def __init__(self):
        pass

    def route_query(self, query: str) -> List[Dict]:
        """
        Route the query to one or more retrievers and aggregate results.
        """
        query_lower = query.lower()
        results = []

        # If query looks medical → PubMed + Arxiv
        if any(keyword in query_lower for keyword in ["disease", "treatment", "drug", "symptom", "therapy", "cancer", "vaccine", "covid19", "diabetes", "tumor"]):
            results.extend(retrievers.pubmed_search(query, k=5))
            results.extend(retrievers.arxiv_search(query, k=5))

        # If query looks general knowledge → Wikipedia
        elif any(keyword in query_lower for keyword in ["history", "definition", "overview", "explain", "who is", "what is"]):
            results.extend(retrievers.wiki_search(query, k=3))

        # Default → aggregate from all three sources
        else:
            results.extend(retrievers.pubmed_search(query, k=3))
            results.extend(retrievers.arxiv_search(query, k=3))
            results.extend(retrievers.wiki_search(query, k=2))

        return results
