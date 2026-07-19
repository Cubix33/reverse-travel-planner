from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .groq_client import explain_match, parse_experience_query
from .matcher import get_destination, load_destinations, recommend, score_destination
from .models import ExperienceSearchRequest, ExplainRequest, TripPreferences

load_dotenv()

app = FastAPI(
    title="Reverse Travel Planner",
    description="Don't choose a destination. Choose the experience.",
    version="0.1.0",
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


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "destinations": len(load_destinations()),
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
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
    }


@app.post("/api/recommend")
async def recommend_destinations(prefs: TripPreferences):
    result = recommend(prefs, limit=5)
    return result


@app.post("/api/explain")
async def explain(req: ExplainRequest):
    result = recommend(req.preferences, limit=20)
    match = next((m for m in result.matches if m.id == req.destination_id), None)
    if not match:
        dest = get_destination(req.destination_id)
        if not dest:
            raise HTTPException(status_code=404, detail="Destination not found")
        match = score_destination(dest, req.preferences)
        if not match:
            raise HTTPException(status_code=404, detail="Destination filtered out by constraints")
    text = await explain_match(match, req.preferences)
    return {"destination_id": req.destination_id, "explanation": text, "match": match}


@app.post("/api/experience-search")
async def experience_search(req: ExperienceSearchRequest):
    extracted = await parse_experience_query(req.query)
    prefs = TripPreferences(
        budget_inr=req.budget_inr,
        days=req.days,
        starting_city=req.starting_city,
        passport=req.passport,
        travel_styles=extracted.get("travel_styles") or ["Nature", "Cafes", "Photography"],
        avoid=extracted.get("avoid") or [],
        pace=extracted.get("pace") or "moderate",
        weather_min_c=int(extracted.get("weather_min_c", 12)),
        weather_max_c=int(extracted.get("weather_max_c", 28)),
        companion="solo",
        max_flight_hours=req.max_flight_hours,
        experience_query=req.query,
    )
    result = recommend(prefs, limit=5)
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
        }
        for d in load_destinations()
    ]
