from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .models import (
    DestinationMatch,
    DimensionScore,
    MatchReason,
    RecommendResponse,
    TripPreferences,
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "destinations.json"

STYLE_TO_GENOME = {
    "nature": "nature",
    "cafes": "cafes",
    "photography": "photography",
    "history": "history",
    "relaxation": "relaxation",
    "nightlife": "nightlife",
    "trekking": "trekking",
    "beach": "beach",
    "mountains": "mountains",
    "museums": "museums",
    "food": "cafes",
    "architecture": "architecture",
}

AVOID_TO_GENOME = {
    "crowds": "crowds",
    "nightlife": "nightlife",
    "trekking": "trekking",
    "expensive_food": "expensive_food",
    "beach": "beach",
    "shopping": "shopping",
}

VISA_EASE = {
    "domestic": 100,
    "visa_free": 100,
    "permit": 85,
    "eta": 90,
    "evisa": 85,
    "voa": 80,
    "schengen": 55,
    "required": 40,
}

EXPERIENCE_KEYWORDS = {
    "switzerland": {"mountains": 30, "nature": 25, "expensive_food": -20},
    "cheaper": {"expensive_food": -25},
    "kyoto": {"history": 25, "photography": 20, "cafes": 15, "crowds": -15},
    "less crowded": {"crowds": -35},
    "crowded": {"crowds": -35},
    "cafe": {"cafes": 30, "relaxation": 15},
    "cafés": {"cafes": 30, "relaxation": 15},
    "cafes": {"cafes": 30, "relaxation": 15},
    "books": {"cafes": 25, "relaxation": 25},
    "read": {"cafes": 20, "relaxation": 25},
    "autumn": {"nature": 20, "photography": 20},
    "walkable": {"walkability": 35},
    "beach": {"beach": 30, "relaxation": 15},
    "mountain": {"mountains": 30, "nature": 20},
    "hike": {"trekking": 30, "nature": 20},
    "digital nomad": {"digital_nomad": 30, "internet": 25, "cafes": 15},
    "wifi": {"internet": 30, "digital_nomad": 20},
    "wi-fi": {"internet": 30, "digital_nomad": 20},
    "family": {"family_friendly": 30, "safety": 15},
    "romantic": {"relaxation": 20, "sunset": 20, "nightlife": -10},
    "party": {"nightlife": 35},
    "history": {"history": 30, "architecture": 15},
    "food": {"cafes": 20, "expensive_food": -10},
    "foodie": {"cafes": 25},
    "quiet": {"crowds": -30, "relaxation": 25, "nightlife": -20},
    "hidden": {"crowds": -25},
    "photography": {"photography": 30, "sunset": 15},
}


@lru_cache(maxsize=1)
def load_destinations() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _flight_hours(dest: dict, city: str) -> float:
    flights = dest.get("flight_hours_from", {})
    if city in flights:
        return float(flights[city])
    # nearest known hub fallback
    for hub in ("Delhi", "London", "Singapore", "Dubai", "New York"):
        if hub in flights:
            return float(flights[hub]) + 2.0
    return 12.0


def _visa_status(dest: dict, passport: str) -> str:
    return dest.get("visa", {}).get(passport, dest.get("visa", {}).get("Indian", "required"))


def _estimate_total(dest: dict, days: int, flight_hours: float) -> int:
    daily = dest["avg_daily_cost_inr"]
    # rough flight estimate from duration
    flight_cost = int(4000 + flight_hours * 2200)
    return daily * days + flight_cost


def _budget_breakdown(total: int, days: int) -> dict[str, int]:
    flights = int(total * 0.28)
    hotel = int(total * 0.34)
    food = int(total * 0.18)
    activities = int(total * 0.12)
    transport = total - (flights + hotel + food + activities)
    return {
        "flights": flights,
        "hotel": hotel,
        "food": food,
        "activities": activities,
        "transport": max(transport, 0),
        "per_day": int(total / max(days, 1)),
    }


def _trip_dna(prefs: TripPreferences, top_genomes: list[dict] | None = None) -> dict[str, int]:
    dna = {
        "Explorer": 40,
        "Foodie": 30,
        "Luxury": 20,
        "Adventure": 30,
        "Culture": 35,
        "Photography": 35,
        "Shopping": 20,
        "Relaxation": 35,
    }
    for style in prefs.travel_styles:
        key = style.lower()
        if key in ("nature", "mountains", "beach"):
            dna["Explorer"] += 15
        if key in ("cafes", "food"):
            dna["Foodie"] += 20
        if key == "history":
            dna["Culture"] += 20
        if key == "photography":
            dna["Photography"] += 20
        if key == "relaxation":
            dna["Relaxation"] += 20
        if key in ("trekking", "nightlife"):
            dna["Adventure"] += 15

    if prefs.budget_inr / max(prefs.days, 1) > 10000:
        dna["Luxury"] += 25
    if prefs.pace == "slow":
        dna["Relaxation"] += 15
    if prefs.pace == "fast":
        dna["Explorer"] += 10
        dna["Adventure"] += 10
    if "shopping" in [a.lower() for a in prefs.avoid]:
        dna["Shopping"] = max(5, dna["Shopping"] - 20)
    if "nightlife" in [a.lower() for a in prefs.avoid]:
        dna["Adventure"] = max(10, dna["Adventure"] - 10)

    if top_genomes:
        avg = lambda k: int(sum(g.get(k, 50) for g in top_genomes) / len(top_genomes))
        dna["Photography"] = max(dna["Photography"], avg("photography") - 5)
        dna["Culture"] = max(dna["Culture"], avg("history") - 5)
        dna["Foodie"] = max(dna["Foodie"], avg("cafes") - 10)

    return {k: min(99, max(5, v)) for k, v in dna.items()}


def _experience_boost(query: str | None) -> dict[str, int]:
    if not query:
        return {}
    q = query.lower()
    boost: dict[str, int] = {}
    for phrase, weights in EXPERIENCE_KEYWORDS.items():
        if phrase in q:
            for k, v in weights.items():
                boost[k] = boost.get(k, 0) + v
    return boost


def _dimension_scores(dest: dict, prefs: TripPreferences, total: int, flight_h: float, visa: str) -> list[DimensionScore]:
    g = dest["genome"]
    weather = dest["weather"]
    budget_score = max(0, min(100, int(100 - abs(total - prefs.budget_inr) / max(prefs.budget_inr, 1) * 120)))
    if total <= prefs.budget_inr:
        budget_score = max(budget_score, 85)

    temp = weather["avg_temp_c"]
    if prefs.weather_min_c <= temp <= prefs.weather_max_c:
        weather_score = 95
    else:
        dist = min(abs(temp - prefs.weather_min_c), abs(temp - prefs.weather_max_c))
        weather_score = max(20, 95 - dist * 8)

    crowd_pref = "crowds" in [a.lower() for a in prefs.avoid]
    crowd_score = (100 - g["crowds"]) if crowd_pref else max(40, 100 - abs(g["crowds"] - 50))

    photo = g["photography"]
    food = max(0, 100 - g["expensive_food"] // 2 + g["cafes"] // 3)
    visa_score = VISA_EASE.get(visa, 50)
    travel_score = max(0, min(100, int(100 - (flight_h / max(prefs.max_flight_hours, 1)) * 55)))

    return [
        DimensionScore(label="Budget Match", score=budget_score),
        DimensionScore(label="Weather Match", score=weather_score),
        DimensionScore(label="Crowd Match", score=int(crowd_score)),
        DimensionScore(label="Photography", score=photo),
        DimensionScore(label="Food", score=min(100, int(food))),
        DimensionScore(label="Visa", score=visa_score),
        DimensionScore(label="Travel Time", score=travel_score),
    ]


def _reasons(dest: dict, prefs: TripPreferences, total: int, flight_h: float, visa: str) -> MatchReason:
    g = dest["genome"]
    positive: list[str] = []
    negative: list[str] = []

    if total <= prefs.budget_inr:
        positive.append(f"Within your budget (~₹{total:,} estimated)")
    else:
        over = total - prefs.budget_inr
        negative.append(f"About ₹{over:,} over your stated budget")

    visa_label = {
        "domestic": "No visa needed (domestic)",
        "visa_free": "Visa-free for your passport",
        "eta": "Simple ETA process",
        "evisa": "Easy e-visa process",
        "voa": "Visa on arrival available",
        "permit": "Entry permit required (manageable)",
        "schengen": "Schengen visa required",
        "required": "Visa required in advance",
    }
    if visa in ("domestic", "visa_free", "eta", "evisa", "voa", "permit"):
        positive.append(visa_label[visa])
    else:
        negative.append(visa_label.get(visa, "Visa process may be involved"))

    temp = dest["weather"]["avg_temp_c"]
    if prefs.weather_min_c <= temp <= prefs.weather_max_c:
        positive.append(f"Average temperature around {temp}°C")
    else:
        negative.append(f"Typical temps around {temp}°C may miss your preferred range")

    for style in prefs.travel_styles:
        key = STYLE_TO_GENOME.get(style.lower())
        if key and g.get(key, 0) >= 75:
            positive.append(f"Strong match for {style.lower()}")
        elif key and g.get(key, 0) < 45:
            negative.append(f"Weaker for {style.lower()}")

    for avoid in prefs.avoid:
        key = AVOID_TO_GENOME.get(avoid.lower().replace(" ", "_"))
        if not key:
            continue
        if g.get(key, 50) <= 40:
            positive.append(f"Low {avoid.lower()} relative to tourist hotspots")
        elif g.get(key, 50) >= 70:
            negative.append(f"Higher {avoid.lower()} than ideal")

    if flight_h <= prefs.max_flight_hours:
        if flight_h <= prefs.max_flight_hours * 0.75:
            positive.append(f"Flight time ~{flight_h:.1f}h from {prefs.starting_city}")
        else:
            positive.append(f"Fits your max flight window (~{flight_h:.1f}h)")
    else:
        negative.append(f"Flight ~{flight_h:.1f}h exceeds your {prefs.max_flight_hours:.0f}h preference")

    if g.get("cafes", 0) >= 85 and "cafes" in [s.lower() for s in prefs.travel_styles]:
        positive.append("Strong café culture")
    if g.get("photography", 0) >= 90:
        positive.append("Excellent photography spots")

    return MatchReason(positive=positive[:6], negative=negative[:4])


def score_destination(dest: dict, prefs: TripPreferences) -> DestinationMatch | None:
    flight_h = _flight_hours(dest, prefs.starting_city)
    visa = _visa_status(dest, prefs.passport)
    total = _estimate_total(dest, prefs.days, flight_h)
    g = dest["genome"]
    boost = _experience_boost(prefs.experience_query)

    # Soft hard-filters: keep but heavily penalize
    penalty = 0.0
    if flight_h > prefs.max_flight_hours * 1.35:
        return None
    if flight_h > prefs.max_flight_hours:
        penalty += 12 + (flight_h - prefs.max_flight_hours) * 4

    if total > prefs.budget_inr * 1.45:
        return None
    if total > prefs.budget_inr:
        penalty += 8 + ((total - prefs.budget_inr) / prefs.budget_inr) * 25

    if visa == "required" and prefs.days <= 4:
        penalty += 8

    style_scores = []
    for style in prefs.travel_styles:
        key = STYLE_TO_GENOME.get(style.lower())
        if key:
            style_scores.append(g.get(key, 50))
    style_avg = sum(style_scores) / len(style_scores) if style_scores else 60

    avoid_pen = 0.0
    for avoid in prefs.avoid:
        key = AVOID_TO_GENOME.get(avoid.lower().replace(" ", "_"))
        if key:
            avoid_pen += max(0, g.get(key, 50) - 40) * 0.35

    temp = dest["weather"]["avg_temp_c"]
    if prefs.weather_min_c <= temp <= prefs.weather_max_c:
        weather_score = 95
    else:
        dist = min(abs(temp - prefs.weather_min_c), abs(temp - prefs.weather_max_c))
        weather_score = max(25, 90 - dist * 7)

    visa_score = VISA_EASE.get(visa, 50)
    budget_ratio = total / max(prefs.budget_inr, 1)
    budget_score = 100 if budget_ratio <= 0.85 else max(25, 100 - (budget_ratio - 0.85) * 120)
    flight_score = max(0, 100 - (flight_h / max(prefs.max_flight_hours, 1)) * 55)

    pace_score = 70
    if prefs.pace == "slow":
        pace_score = (g["relaxation"] + (100 - g["nightlife"])) / 2
    elif prefs.pace == "fast":
        pace_score = (g.get("walkability", 50) + g.get("public_transport", 50) + g["nightlife"]) / 3

    companion_score = 70
    if prefs.companion == "family":
        companion_score = g["family_friendly"]
    elif prefs.companion == "solo":
        companion_score = (g["safety"] + g.get("walkability", 60)) / 2
    elif prefs.companion == "friends":
        companion_score = (g["nightlife"] + g.get("cafes", 60)) / 2
    elif prefs.companion == "partner":
        companion_score = (g["relaxation"] + g.get("sunset", 60) + g["photography"]) / 3

    boost_score = 0.0
    if boost:
        vals = []
        for k, w in boost.items():
            base = g.get(k, 50)
            # negative weights mean we want LOW values of that attribute
            if w < 0:
                vals.append((100 - base) * (abs(w) / 30))
            else:
                vals.append(base * (w / 30))
        boost_score = sum(vals) / len(vals)

    raw = (
        style_avg * 0.28
        + budget_score * 0.18
        + weather_score * 0.12
        + visa_score * 0.12
        + flight_score * 0.12
        + pace_score * 0.06
        + companion_score * 0.06
        + boost_score * 0.06
        - avoid_pen
        - penalty
    )
    match_percent = int(max(40, min(99, raw)))

    dims = _dimension_scores(dest, prefs, total, flight_h, visa)
    reasons = _reasons(dest, prefs, total, flight_h, visa)
    highlights = {
        k: g[k]
        for k in (
            "walkability",
            "internet",
            "safety",
            "digital_nomad",
            "beach",
            "mountains",
            "crowds",
            "sunset",
        )
        if k in g
    }

    return DestinationMatch(
        id=dest["id"],
        name=dest["name"],
        country=dest["country"],
        region=dest["region"],
        tagline=dest["tagline"],
        match_percent=match_percent,
        dimensions=dims,
        reasons=reasons,
        hidden_gems=dest.get("hidden_gems", [])[:3],
        estimated_total_inr=total,
        flight_hours=flight_h,
        visa_status=visa,
        avg_temp_c=temp,
        budget_breakdown=_budget_breakdown(total, prefs.days),
        trip_dna={},
        genome_highlights=highlights,
    )


def recommend(prefs: TripPreferences, limit: int = 5) -> RecommendResponse:
    scored: list[DestinationMatch] = []
    for dest in load_destinations():
        match = score_destination(dest, prefs)
        if match:
            scored.append(match)

    scored.sort(key=lambda m: m.match_percent, reverse=True)
    top = scored[:limit]

    # attach DNA based on prefs + top genomes
    top_genomes = []
    dest_by_id = {d["id"]: d for d in load_destinations()}
    for m in top:
        top_genomes.append(dest_by_id[m.id]["genome"])
    dna = _trip_dna(prefs, top_genomes)
    for m in top:
        m.trip_dna = dna

    styles = ", ".join(prefs.travel_styles) if prefs.travel_styles else "open preferences"
    summary = (
        f"{prefs.days}-day trip from {prefs.starting_city} · ₹{prefs.budget_inr:,} · "
        f"{styles} · max {prefs.max_flight_hours:.0f}h flight"
    )
    return RecommendResponse(matches=top, trip_dna=dna, query_summary=summary)


def get_destination(destination_id: str) -> dict | None:
    for dest in load_destinations():
        if dest["id"] == destination_id:
            return dest
    return None
