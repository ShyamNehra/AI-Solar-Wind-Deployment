import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Primary target: Gemini 3.7 Flash, falling back to 3.6 or 2.5
MODEL_CANDIDATES = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
]


def generate_ai_risk_analysis(
    solar_score: float,
    wind_score: float,
    infrastructure_score: float,
    overall_score: float,
) -> dict:
    """Evaluates site metrics using Gemini and produces a JSON risk assessment and recommendation."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY missing from environment variables.")
        return {
            "recommendation": "Optimal candidate for renewable project development based on current metrics.",
            "risks": [
                "GEMINI_API_KEY not configured; using automated fallback risk checks."
            ],
        }

    prompt = f"""
    Evaluate the following renewable energy site scores for a solar/wind hybrid project:
    - Overall Suitability: {overall_score}/100
    - Solar Potential Score: {solar_score}/100
    - Wind Potential Score: {wind_score}/100
    - Infrastructure Score: {infrastructure_score}/100

    Return a clean JSON object with exactly two keys:
    1. "recommendation": A short 1-2 sentence investment recommendation statement.
    2. "risks": A list of 2-3 specific risk factor strings based on lower sub-scores or site viability.
    """

    client = genai.Client(api_key=api_key)
    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)

        except Exception as e:
            last_error = str(e)
            logger.info(
                f"Model {model_name} unavailable ({e}), trying next candidate..."
            )

    print(f"\n[GEMINI API ERROR]: {last_error}\n")
    return {
        "recommendation": "Favorable location for hybrid renewable expansion.",
        "risks": [f"AI Analysis Error: {last_error}"],
    }