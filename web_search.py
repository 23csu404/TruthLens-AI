
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

API_KEY = os.getenv("TAVILY_API_KEY")


def search_claim(claim):
    """Search the live web for evidence about one claim."""

    if not API_KEY:
        raise ValueError("Tavily API key is missing.")

    client = TavilyClient(api_key=API_KEY)

    response = client.search(
        query=claim,
        search_depth="basic",
        max_results=3,
        include_answer=False
    )

    evidence = []

    for result in response.get("results", []):
        evidence.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "score": result.get("score", 0)
        })

    return evidence
