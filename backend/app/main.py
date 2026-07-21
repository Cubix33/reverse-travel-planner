from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .groq_client import explain_match, generate_itinerary, parse_experience_query
from .matcher import get_destination, load_destinations, recommend, score_destination
from .models import (
    CompareRequest,
    ExperienceSearchRequest,
    ExplainRequest,
    ItineraryRequest,
    TripPreferences,
)

load_dotenv()

app = FastAPI(
    title="Reverse Travel Planner",
    description="Don't choose a destination. Choose the experience.",
    version="0.2.0",
)

origins = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_match(destination_id: str, preferences: TripPreferences):
    result = recommend(preferences, limit=40)
    match = next((m for m in result.matches if m.id == destination_id), None)
    if match:
        return match
    dest = get_destination(destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    match = score_destination(dest, preferences)
    if not match:
        raise HTTPException(status_code=404, detail="Destination filtered out by constraints")
    return match


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "destinations": len(load_destinations()),
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "version": "0.2.0",
    }


@app.get("/api/meta")
def meta():
    cities = sorted(
        {
            city
            for d in load_destinations()
            for city in d.get("flight_hours_from", {}).keys()
        }
    )
    return {
        "starting_cities": cities,
        "passports": ["Indian", "US", "UK", "EU", "Singapore"],
        "travel_styles": [
            "Nature",
            "Cafes",
            "Photography",
            "History",
            "Relaxation",
            "Nightlife",
            "Trekking",
            "Beach",
            "Mountains",
            "Museums",
            "Architecture",
        ],
        "avoid_options": ["Crowds", "Nightlife", "Trekking", "Expensive food", "Shopping"],
        "companions": ["solo", "friends", "family", "partner"],
        "paces": ["slow", "moderate", "fast"],
        "experience_examples": [
            "Somewhere like Switzerland but cheaper",
            "Somewhere like Kyoto but less crowded",
            "A place where I can read books in cafés all day",
            "I want to experience autumn in walkable towns",
            "Quiet mountains with good Wi-Fi for remote work",
        ],
    }


@app.post("/api/recommend")
async def recommend_destinations(
    prefs: TripPreferences,
    limit: int = Query(default=8, ge=3, le=15),
):
    return recommend(prefs, limit=limit)


@app.post("/api/explain")
async def explain(req: ExplainRequest):
    match = _resolve_match(req.destination_id, req.preferences)
    text = await explain_match(match, req.preferences)
    return {"destination_id": req.destination_id, "explanation": text, "match": match}


@app.post("/api/itinerary")
async def itinerary(req: ItineraryRequest):
    dest = get_destination(req.destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    match = _resolve_match(req.destination_id, req.preferences)
    plan = await generate_itinerary(dest, match, req.preferences)
    return plan


@app.post("/api/compare")
async def compare(req: CompareRequest):
    rows = []
    for dest_id in req.destination_ids:
        dest = get_destination(dest_id)
        if not dest:
            continue
        match = score_destination(dest, req.preferences)
        if not match:
            # still include with soft score by temporarily loosening via clone prefs
            loose = req.preferences.model_copy(
                update={"max_flight_hours": req.preferences.max_flight_hours * 1.5, "budget_inr": int(req.preferences.budget_inr * 1.5)}
            )
            match = score_destination(dest, loose)
        if match:
            rows.append(
                {
                    "match": match,
                    "genome": dest.get("genome", {}),
                    "weather": dest.get("weather", {}),
                    "hidden_gems": dest.get("hidden_gems", []),
                }
            )
    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="Need at least two comparable destinations")
    rows.sort(key=lambda r: r["match"].match_percent, reverse=True)
    winner = rows[0]["match"].name
    return {"winner": winner, "items": rows}


@app.post("/api/experience-search")
async def experience_search(req: ExperienceSearchRequest):
    extracted = await parse_experience_query(req.query)
    styles = extracted.get("travel_styles") or ["Nature", "Cafes", "Photography"]
    # normalize casing for matcher
    styles = [s.title() if isinstance(s, str) else s for s in styles]
    avoid = extracted.get("avoid") or []
    avoid = [
        a.replace("_", " ").title().replace("Expensive Food", "Expensive food")
        if isinstance(a, str)
        else a
        for a in avoid
    ]
    prefs = TripPreferences(
        budget_inr=req.budget_inr,
        days=req.days,
        starting_city=req.starting_city,
        passport=req.passport,
        travel_styles=styles,
        avoid=avoid,
        pace=extracted.get("pace") or "moderate",
        weather_min_c=int(extracted.get("weather_min_c", 12)),
        weather_max_c=int(extracted.get("weather_max_c", 28)),
        companion="solo",
        max_flight_hours=req.max_flight_hours,
        experience_query=req.query,
    )
    result = recommend(prefs, limit=8)
    return {"extracted": extracted, "preferences": prefs, "result": result}


@app.get("/api/destinations")
def list_destinations():
    return [
        {
            "id": d["id"],
            "name": d["name"],
            "country": d["country"],
            "region": d["region"],
            "tagline": d["tagline"],
            "avg_daily_cost_inr": d["avg_daily_cost_inr"],
            "avg_temp_c": d.get("weather", {}).get("avg_temp_c"),
        }
        for d in load_destinations()
    ]


@app.get("/api/destinations/{destination_id}")
def destination_detail(destination_id: str):
    dest = get_destination(destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest
