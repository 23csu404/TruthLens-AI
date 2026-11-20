
import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key is missing.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash"


def verify_claims_batch(claims_with_evidence):
    """Verify multiple claims in one Gemini request."""

    if not claims_with_evidence:
        return []

    prompt = f"""
You are a professional fact-checking analyst.

Verify every claim using only the web evidence supplied
for that claim.

INPUT:
{json.dumps(claims_with_evidence, ensure_ascii=False)}

Allowed verdicts:
- Verified
- Inaccurate
- False
- Insufficient Evidence

Rules:
1. Verified means reliable evidence supports the claim.
2. Inaccurate means the claim is outdated, partly correct,
   misleading or missing important context.
3. False requires reliable evidence directly contradicting it.
4. Insufficient Evidence means the evidence is inadequate.
5. Lack of evidence does not prove a claim false.
6. Never invent statistics, facts or source URLs.
7. Use only the evidence supplied for each claim.
8. Return one result for every input claim.
9. Preserve the original claim ID.

Return ONLY valid JSON in this format:

{{
    "results": [
        {{
            "id": 0,
            "verdict": "Verified",
            "explanation": "Evidence-based explanation",
            "corrected_fact": "Correction or Not required",
            "sources": [
                {{
                    "title": "Source title",
                    "url": "https://example.com"
                }}
            ]
        }}
    ]
}}
"""

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            result = response.text.strip()

            if result.startswith("```"):
                result = result.split("\n", 1)[1]
                result = result.rsplit("```", 1)[0].strip()

            data = json.loads(result)
            results = data.get("results", [])

            valid_verdicts = {
                "Verified",
                "Inaccurate",
                "False",
                "Insufficient Evidence"
            }

            cleaned = {}

            for item in results:
                claim_id = item.get("id")
                verdict = item.get("verdict")

                if (
                    isinstance(claim_id, int)
                    and verdict in valid_verdicts
                ):
                    cleaned[claim_id] = item

            final_results = []

            for original in claims_with_evidence:
                claim_id = original["id"]

                final_results.append(
                    cleaned.get(
                        claim_id,
                        {
                            "id": claim_id,
                            "verdict": "Insufficient Evidence",
                            "explanation": (
                                "No valid verification result was returned."
                            ),
                            "corrected_fact": "Not established",
                            "sources": []
                        }
                    )
                )

            return final_results

        except Exception:
            if attempt == 1:
                raise

            time.sleep(2)

    return []
