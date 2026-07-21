from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

from .itinerary import build_fallback_itinerary
from .models import DestinationMatch, TripPreferences

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def _chat(
    messages: list[dict[str, str]],
    temperature: float = 0.4,
    max_tokens: int = 700,
) -> str | None:
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
        "max_tokens": max_tokens,
    }
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(GROQ_URL, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _extract_json(text: str) -> Any | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", cleaned)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
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


def _keyword_experience_parse(query: str) -> dict[str, Any]:
    q = query.lower()
    styles: list[str] = []
    avoid: list[str] = []
    pace = "moderate"
    weather_min_c, weather_max_c = 12, 28

    mapping = [
        (("cafe", "café", "coffee", "books", "read"), "Cafes"),
        (("photo", "instagram", "sunset"), "Photography"),
        (("history", "temple", "museum", "heritage", "kyoto"), "History"),
        (("nature", "forest", "park", "switzerland", "green"), "Nature"),
        (("beach", "ocean", "sea", "coast"), "Beach"),
        (("mountain", "hike", "trek", "alpine"), "Mountains"),
        (("relax", "slow", "calm", "quiet"), "Relaxation"),
        (("night", "party", "bar"), "Nightlife"),
        (("architecture", "design", "building"), "Architecture"),
    ]
    for keys, label in mapping:
        if any(k in q for k in keys):
            styles.append(label)

    if any(k in q for k in ("crowd", "tourist trap", "less crowded", "quiet", "hidden")):
        avoid.append("Crowds")
    if "expensive" in q or "cheaper" in q or "budget" in q:
        avoid.append("Expensive food")
    if "no trek" in q or "not hike" in q:
        avoid.append("Trekking")
    if "no night" in q:
        avoid.append("Nightlife")

    if any(k in q for k in ("slow", "read", "linger", "unhurried")):
        pace = "slow"
    elif any(k in q for k in ("packed", "see everything", "fast")):
        pace = "fast"

    if "autumn" in q or "fall" in q:
        weather_min_c, weather_max_c = 10, 20
    if "summer" in q or "warm" in q:
        weather_min_c, weather_max_c = 22, 32
    if "cool" in q or "cold" in q:
        weather_min_c, weather_max_c = 5, 18

    # Title-case styles already; ensure unique
    styles = list(dict.fromkeys(styles)) or ["Nature", "Cafes", "Photography"]
    avoid = list(dict.fromkeys(avoid))
    return {
        "travel_styles": styles,
        "avoid": avoid,
        "pace": pace,
        "weather_min_c": weather_min_c,
        "weather_max_c": weather_max_c,
        "notes": query,
    }


async def parse_experience_query(query: str) -> dict[str, Any]:
    """Use Groq to extract structured prefs; keyword fallback always available."""
    default = _keyword_experience_parse(query)
    if not GROQ_API_KEY:
        return default

    prompt = f"""Extract travel preferences from this experience search.
Return ONLY valid JSON with keys:
travel_styles (array from: Nature, Cafes, Photography, History, Relaxation, Nightlife, Trekking, Beach, Mountains, Museums, Architecture),
avoid (array from: Crowds, Nightlife, Trekking, Expensive food, Shopping),
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
    data = _extract_json(text)
    if not isinstance(data, dict):
        return default
    return {**default, **data}


async def generate_itinerary(dest: dict, match: DestinationMatch, prefs: TripPreferences) -> dict:
    fallback = build_fallback_itinerary(dest, match, prefs)
    if not GROQ_API_KEY:
        return fallback

    prompt = f"""Create a practical day-by-day itinerary as JSON only.
Keys:
summary (string),
days: array of {{day:int, title:string, focus:string, activities:[{{time, title, note}}]}},
concierge: array of {{trigger, action}} for weather/crowd swaps during the trip,
packing_tips: string array.

Constraints:
- Exactly {prefs.days} days
- Pace: {prefs.pace}; companion: {prefs.companion}
- Styles: {', '.join(prefs.travel_styles)}
- Avoid: {', '.join(prefs.avoid) or 'none'}
- Budget about ₹{prefs.budget_inr:,}
- Destination: {match.name}, {match.country}
- Include at least one hidden gem from: {match.hidden_gems}
- Favor local, low-tourist-trap ideas
- 2-4 activities per day
No markdown."""

    text = await _chat(
        [
            {"role": "system", "content": "You are a concise travel concierge. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=1600,
    )
    if not text:
        return fallback
    data = _extract_json(text)
    if not isinstance(data, dict) or not data.get("days"):
        return fallback
    return {
        "destination_id": dest["id"],
        "destination_name": match.name,
        "summary": data.get("summary") or fallback["summary"],
        "days": data.get("days") or fallback["days"],
        "concierge": data.get("concierge") or fallback["concierge"],
        "packing_tips": data.get("packing_tips") or fallback["packing_tips"],
        "source": "groq",
    }
