from __future__ import annotations

from .models import DestinationMatch, TripPreferences


STYLE_ACTIVITIES = {
    "nature": ["Scenic viewpoint walk", "Local park or garden visit", "Golden-hour landscape stop"],
    "cafes": ["Specialty coffee crawl", "Long-form café reading morning", "Neighborhood bakery stop"],
    "photography": ["Sunrise photo walk", "Architecture details hunt", "Blue-hour city overlook"],
    "history": ["Old-town heritage loop", "Museum or palace visit", "Local guide story walk"],
    "relaxation": ["Slow morning at a quiet café", "Spa or wellness block", "Sunset with nowhere to rush"],
    "nightlife": ["Local music bar", "Night market wander", "Late dessert spot"],
    "trekking": ["Half-day trail", "Foothill viewpoint hike", "Easy ridgeline walk"],
    "beach": ["Morning swim", "Coastal walk", "Beachside dinner"],
    "mountains": ["Valley viewpoint", "Cable car or lookout", "Mountain café stop"],
    "museums": ["Flagship museum", "Small gallery visit", "Design or craft exhibit"],
    "architecture": ["Landmark exterior circuit", "Neighborhood facade walk", "Iconic interior visit"],
}

PACE_SLOTS = {
    "slow": ["Morning", "Late afternoon"],
    "moderate": ["Morning", "Afternoon", "Evening"],
    "fast": ["Morning", "Midday", "Afternoon", "Evening"],
}


def _pick_activities(prefs: TripPreferences, dest: dict, day_index: int) -> list[dict]:
    g = dest["genome"]
    styles = [s.lower() for s in prefs.travel_styles] or ["cafes", "photography", "relaxation"]
    slots = PACE_SLOTS.get(prefs.pace, PACE_SLOTS["moderate"])
    gems = dest.get("hidden_gems", [])
    activities = []

    for i, slot in enumerate(slots):
        style = styles[(day_index + i) % len(styles)]
        pool = STYLE_ACTIVITIES.get(style, STYLE_ACTIVITIES["relaxation"])
        title = pool[(day_index + i) % len(pool)]
        if i == len(slots) - 1 and gems:
            title = gems[day_index % len(gems)]
            note = "Hidden gem — usually quieter than the headline sights"
        else:
            note = f"Matched to your {style} preference"
            if style == "nature" and g.get("nature", 0) < 50:
                note = "Soft nature option near the city core"
        activities.append({"time": slot, "title": title, "note": note})

    if "crowds" in [a.lower() for a in prefs.avoid]:
        activities.insert(
            0,
            {
                "time": "Tip",
                "title": "Start before 9 AM on popular sights",
                "note": "Keeps you ahead of peak tourist flow",
            },
        )
    return activities


def build_fallback_itinerary(dest: dict, match: DestinationMatch, prefs: TripPreferences) -> dict:
    days = []
    for i in range(prefs.days):
        theme = "Arrive & settle" if i == 0 else ("Deep dive" if i < prefs.days - 1 else "Soft exit day")
        days.append(
            {
                "day": i + 1,
                "title": f"Day {i + 1}: {theme}",
                "focus": dest["tagline"] if i == 0 else f"{match.name} at your pace",
                "activities": _pick_activities(prefs, dest, i),
            }
        )

    rain = dest.get("weather", {}).get("rain_probability", 0.3)
    concierge = []
    if rain >= 0.4:
        concierge.append(
            {
                "trigger": "Rain likely",
                "action": "Swap outdoor viewpoints for museums, covered markets, or long café sessions",
            }
        )
    if prefs.pace == "slow":
        concierge.append(
            {
                "trigger": "Energy dip",
                "action": "Keep one unscheduled block each afternoon — this destination rewards lingering",
            }
        )
    else:
        concierge.append(
            {
                "trigger": "Transit delay",
                "action": "Use walkable backup stops within 15 minutes of your hotel area",
            }
        )
    if match.hidden_gems:
        concierge.append(
            {
                "trigger": "Crowds building",
                "action": f"Pivot to: {match.hidden_gems[0]}",
            }
        )

    return {
        "destination_id": dest["id"],
        "destination_name": match.name,
        "summary": (
            f"A {prefs.days}-day {prefs.pace} plan in {match.name} for a {prefs.companion} trip, "
            f"tuned to {', '.join(prefs.travel_styles[:3]) or 'your preferences'}."
        ),
        "days": days,
        "concierge": concierge,
        "packing_tips": _packing_tips(dest, prefs),
        "source": "fallback",
    }


def _packing_tips(dest: dict, prefs: TripPreferences) -> list[str]:
    temp = dest.get("weather", {}).get("avg_temp_c", 20)
    tips = []
    if temp < 15:
        tips.append("Light layers and a windproof jacket")
    elif temp > 26:
        tips.append("Breathable clothes, sunscreen, refillable bottle")
    else:
        tips.append("Versatile layers for mild swings")
    if dest.get("genome", {}).get("walkability", 50) >= 75:
        tips.append("Comfortable walking shoes — this city rewards being on foot")
    if "photography" in [s.lower() for s in prefs.travel_styles]:
        tips.append("Extra battery / memory — sunrise and blue hour both pay off here")
    if prefs.companion == "family":
        tips.append("Keep one low-effort backup activity near your stay each day")
    return tips[:4]
