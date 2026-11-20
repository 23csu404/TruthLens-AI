
import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    import streamlit as st
    API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found in .env file")

client = genai.Client(api_key=API_KEY)


def extract_claims(document_text):

    prompt = f"""
    You are an expert fact-checking assistant.

    Read the following document and extract individual
    factual claims that can be verified using external sources.

    Focus on:
    - Statistics and numerical claims
    - Dates and historical statements
    - Scientific and technical claims
    - Financial and business claims

    Do not extract headings, opinions or general instructions.

    Return ONLY valid JSON in this format:

    {{
        "claims": [
            {{
                "claim": "Individual factual statement",
                "category": "Science",
                "importance": "High"
            }}
        ]
    }}

    DOCUMENT:
    {document_text}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    result = response.text.strip()

    if result.startswith("```"):
        result = result.split("\n", 1)[1]
        result = result.rsplit("```", 1)[0].strip()

    data = json.loads(result)

    return data.get("claims", [])
