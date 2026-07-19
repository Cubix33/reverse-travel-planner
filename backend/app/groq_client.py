from __future__ import annotations

import json
import os
from typing import Any

import httpx
from dotenv import load_dotenv

from .models import DestinationMatch, TripPreferences

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def _chat(messages: list[dict[str, str]], temperature: float = 0.4) -> str | None:
    if not GROQ_API_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 700,
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(GROQ_URL, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def fallback_explanation(match: DestinationMatch, prefs: TripPreferences) -> str:
    pos = "\n".join(f"✅ {p}" for p in match.reasons.positive)
    neg = "\n".join(f"❌ {n}" for n in match.reasons.negative) if match.reasons.negative else ""
    gems = "\n".join(f"• {g}" for g in match.hidden_gems)
    return (
        f"We recommended {match.name} because it scored {match.match_percent}% "
        f"against your {prefs.days}-day trip from {prefs.starting_city}.\n\n"
        f"{pos}\n{neg}\n\n"
        f"Hidden gems locals love:\n{gems}"
    ).strip()


async def explain_match(match: DestinationMatch, prefs: TripPreferences) -> str:
    prompt = f"""You are the explainability engine for Reverse Travel Planner.
Write a concise, warm recommendation explanation (120-180 words) for why this destination fits.

User prefs:
- Budget: ₹{prefs.budget_inr:,} for {prefs.days} days from {prefs.starting_city}
- Passport: {prefs.passport}
- Styles: {', '.join(prefs.travel_styles) or 'none'}
- Avoid: {', '.join(prefs.avoid) or 'none'}
- Pace: {prefs.pace}, companion: {prefs.companion}
- Weather: {prefs.weather_min_c}-{prefs.weather_max_c}°C
- Max flight: {prefs.max_flight_hours}h
- Experience query: {prefs.experience_query or 'n/a'}

Destination:
- {match.name}, {match.country} ({match.match_percent}% match)
- Est. total: ₹{match.estimated_total_inr:,}, flight {match.flight_hours}h, visa: {match.visa_status}
- Temp: {match.avg_temp_c}°C
- Pros: {match.reasons.positive}
- Cons: {match.reasons.negative}
- Hidden gems: {match.hidden_gems}

Format:
Start with one sentence "We recommended X because..."
Then 4-6 short bullet lines starting with ✅ or ❌
End with one sentence about a hidden gem.
No markdown headings. No fluff."""

    text = await _chat(
        [
            {"role": "system", "content": "You explain travel recommendations clearly and specifically."},
            {"role": "user", "content": prompt},
        ]
    )
    return text or fallback_explanation(match, prefs)


async def parse_experience_query(query: str) -> dict[str, Any]:
    """Use Groq to extract structured prefs from a feeling-based search. Falls back to empty."""
    default: dict[str, Any] = {
        "travel_styles": [],
        "avoid": [],
        "pace": "moderate",
        "weather_min_c": 12,
        "weather_max_c": 28,
        "notes": query,
    }
    if not GROQ_API_KEY:
        return default

    prompt = f"""Extract travel preferences from this experience search.
Return ONLY valid JSON with keys:
travel_styles (array from: nature, cafes, photography, history, relaxation, nightlife, trekking, beach, mountains, museums, architecture),
avoid (array from: crowds, nightlife, trekking, expensive_food, shopping),
pace (slow|moderate|fast),
weather_min_c (int),
weather_max_c (int),
notes (short string).

Query: {query}"""

    text = await _chat(
        [
            {"role": "system", "content": "Return only JSON. No markdown."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    if not text:
        return default
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
        return {**default, **data}
    except Exception:
        return default
