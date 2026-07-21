# Reverse Travel Planner

### Don't choose a destination. Choose the experience.

Most travel apps ask *where* you want to go.  
**Reverse Travel Planner** asks *what kind of trip you want* — budget, days, visa friction, weather, pace, vibes — and returns **ranked destinations** with explainable match scores.

Built for **OpenAI Build Week** as a runnable product: constraint matching, Destination Genome, Trip DNA, What If mode, experience search, compare, itineraries, AI Concierge, and Travel Twin.

> Other tools answer: “What should I do in Paris?”  
> This answers: “Given who you are and your constraints, **where should you go in the first place?**”

---

## Why this idea

Travelers often know constraints and feelings, not a city:

- I have ₹40k and 5 days  
- I don’t want a visa headache  
- I hate tourist traps  
- I want cafés, cool weather, and a short flight  

**The destination is the output, not the input.** That makes this a richer AI problem: constraint satisfaction + personalization + recommendation + explainable AI — not another itinerary rewriter.

---

## Features

| Feature | What you get |
| --- | --- |
| Ideal-trip form | Budget, days, city, passport, styles, avoids, pace, weather, companion, flight cap |
| Experience search | Natural-language vibes (“Kyoto but less crowded”) |
| Ranked matches | Global destinations with % match |
| Explainability | Spotify-style dimension bars + ✅/❌ reasons + optional LLM narrative |
| Destination Genome | Multi-attribute feature vectors (walkability, crowds, cafés, visa ease…) |
| Trip DNA | Explorer / Foodie / Culture / Photography profile from the search |
| What If mode | Drag budget / days / flight → live re-ranking |
| Compare | Side-by-side up to 3 destinations |
| Itinerary + Concierge | Day-by-day plan + rain/crowd swap tips |
| Smart budget split | Flights, hotel, food, activities, transport |
| Hidden gems | Local-leaning spots, not only landmarks |
| Travel Twin + Saves | Persistent learning and shortlists (localStorage) |

---

## Tech stack

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | React + Vite | Fast product UI for a web demo |
| Backend | FastAPI | Typed APIs, quick iteration |
| Ranking | Rules + Destination Genome vectors | Deterministic, explainable, works offline |
| LLM | Groq (`llama-3.3-70b-versatile`) | Explanations, experience parsing, itineraries |
| Sample data | `backend/data/destinations.json` | No paid travel APIs required |
| Persistence | Browser `localStorage` | Twin + saves without auth |

---

## Prerequisites

- Python 3.11+ (3.12 tested)
- Node.js 18+ and npm
- Optional: Groq API key (app runs fully without it)

---

## Setup

```bash
git clone https://github.com/<your-username>/reverse-travel-planner.git
cd reverse-travel-planner

# backend
cd backend
python -m pip install -r requirements.txt
cp .env.example .env          # Windows: Copy-Item .env.example .env

# frontend
cd ../frontend
npm install
```

Edit `backend/.env` (optional Groq key):

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## Running the project

**Terminal A — API**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal B — UI**
```bash
cd frontend
npm run dev
```

- App: **http://localhost:5173**
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

Vite proxies `/api/*` → port `8000`.

**Sample API call:**

```bash
curl -X POST "http://127.0.0.1:8000/api/recommend?limit=5" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_inr": 40000,
    "days": 5,
    "starting_city": "Delhi",
    "passport": "Indian",
    "travel_styles": ["Nature", "Cafes", "Photography"],
    "avoid": ["Crowds"],
    "pace": "slow",
    "weather_min_c": 15,
    "weather_max_c": 28,
    "companion": "solo",
    "max_flight_hours": 6
  }'
```

---

## Sample data

No database setup. All ranking runs on a curated file:

**[`backend/data/destinations.json`](backend/data/destinations.json)** — ~38 destinations across Asia, Europe, Americas, Africa, and Oceania.

Costs, flight times, and visa labels are **approximate demo values** for matching — not live booking quotes.

### What’s in each destination

| Field | Purpose in the engine |
| --- | --- |
| `avg_daily_cost_inr` | Budget fit + smart budget split |
| `flight_hours_from` | Travel-time filter from Delhi, Mumbai, Bangalore, London, New York, Singapore, Dubai |
| `visa` | Ease score by passport (`visa_free`, `evisa`, `schengen`, `required`, …) |
| `weather` | Temp / rain match against user range |
| `genome` | 22-attribute feature vector (0–100) used for style, avoid, pace, companion scoring |
| `hidden_gems` | Shown in UI + woven into itineraries |

**Genome attributes:** nature, cafes, photography, history, relaxation, nightlife, trekking, crowds, expensive_food, beach, mountains, walkability, museums, architecture, internet, safety, vegetarian, digital_nomad, family_friendly, public_transport, sunset, shopping.

### Example record (Chiang Mai)

```json
{
  "id": "chiang_mai",
  "name": "Chiang Mai",
  "country": "Thailand",
  "region": "Southeast Asia",
  "tagline": "Temples, cafés, and mountain air",
  "avg_daily_cost_inr": 2800,
  "flight_hours_from": {
    "Delhi": 5.5,
    "Mumbai": 5.0,
    "Bangalore": 4.5,
    "London": 13.0,
    "New York": 20.0,
    "Singapore": 2.5,
    "Dubai": 7.0
  },
  "visa": {
    "Indian": "visa_free",
    "US": "visa_free",
    "UK": "visa_free",
    "EU": "visa_free",
    "Singapore": "visa_free"
  },
  "weather": {
    "avg_temp_c": 26,
    "rain_probability": 0.3,
    "air_quality": 55
  },
  "genome": {
    "nature": 85,
    "cafes": 95,
    "photography": 88,
    "history": 80,
    "relaxation": 90,
    "nightlife": 50,
    "trekking": 70,
    "crowds": 40,
    "expensive_food": 15,
    "beach": 5,
    "mountains": 80,
    "walkability": 70,
    "museums": 50,
    "architecture": 75,
    "internet": 88,
    "safety": 80,
    "vegetarian": 85,
    "digital_nomad": 98,
    "family_friendly": 75,
    "public_transport": 55,
    "sunset": 80,
    "shopping": 60
  },
  "hidden_gems": [
    "Mae Kampong village cafés",
    "Wat Umong forest temple",
    "Nimman side-street specialty coffee"
  ]
}
```

### Coverage (sample set)

| Region | Examples |
| --- | --- |
| South / SE Asia | Chiang Mai, Hanoi, Da Nang, Bali, Singapore, Luang Prabang, Goa, Munnar, Sikkim, Jaipur, Sri Lanka, Bhutan |
| East Asia | Kyoto, Tokyo, Seoul |
| Europe | Lisbon, Porto, Prague, Budapest, Barcelona, Edinburgh, Dublin, Valletta, Kraków, Reykjavik |
| Caucasus / Central Asia | Tbilisi, Almaty, Istanbul |
| Americas | Mexico City, Medellín, Cusco, Vancouver |
| Africa / Oceania | Cape Town, Cairo, Marrakech, Zanzibar, Queenstown, Hobart |

### How sample prefs map onto this data

Demo search: **Delhi · ₹40,000 · 5 days · Nature + Cafés + Photography · Avoid Crowds · max 6h flight**

Typically surfaces budget-friendly, café-heavy, lower-crowd options within flight range (e.g. Chiang Mai, Sikkim, Sri Lanka, Munnar) because:

- daily cost × days + estimated flight stays near budget  
- `genome.cafes` / `nature` / `photography` are high  
- `genome.crowds` is relatively low  
- `flight_hours_from.Delhi` ≤ ~6h (soft penalty beyond)

### Adding your own destination

1. Copy any object in `destinations.json`
2. Give it a unique `id`
3. Fill hubs you care about in `flight_hours_from` (missing hubs fall back with a small penalty)
4. Score `genome` fields 0–100 (higher = stronger presence of that trait; for `crowds` / `expensive_food`, higher means *more* of that thing)
5. Restart the API — no migrations

Inspect live via `GET /api/destinations` or `GET /api/destinations/chiang_mai`.

---

## API reference

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Status + Groq configured |
| `GET` | `/api/meta` | Form options |
| `POST` | `/api/recommend` | Rank destinations |
| `POST` | `/api/experience-search` | Feeling → matches |
| `POST` | `/api/explain` | Narrative “why” |
| `POST` | `/api/itinerary` | Day plan + concierge |
| `POST` | `/api/compare` | Side-by-side scores |
| `GET` | `/api/destinations` | Catalog |
| `GET` | `/api/destinations/{id}` | Full record |

---

## Project structure

```text
reverse-travel-planner/
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── data/destinations.json     # sample Destination Genome
│   └── app/
│       ├── main.py                # FastAPI routes
│       ├── models.py
│       ├── matcher.py             # hybrid ranking + explainability
│       ├── itinerary.py           # itinerary / concierge fallback
│       └── groq_client.py         # Groq + offline fallbacks
└── frontend/
    ├── vite.config.js             # proxies /api → :8000
    └── src/
        ├── App.jsx
        ├── api.js / storage.js    # Twin + saved trips
        └── components/
```

---

## How Codex & GPT-5.6 accelerated this build

### Where they mattered

| Phase | Role | Outcome |
| --- | --- | --- |
| Problem framing | Stress-tested “another itinerary app” vs reverse matching | Locked wedge: **destination as output** |
| Architecture | Hybrid stack (rules + genome + LLM explanations) | `matcher.py` ranks; LLM narrates / enriches |
| Scaffolding | FastAPI + Vite React, env, CORS, proxy | Runnable dual-server app quickly |
| Sample data | Genome schema + seeded global cities | `destinations.json` |
| Core engine | Scoring, filters, dimensions, Trip DNA, budget split | Non-trivial recommend path offline |
| Product surface | Form → results → What If → compare → itinerary → Twin | Coherent product, not a single API demo |
| Reliability | Graceful Groq fallbacks | Demo never hard-fails without a key |

### Codex specifically accelerated

1. **Multi-file vertical slices** — features landed across models → matcher/LLM → React → CSS in one pass  
2. **Recommendation as real software** — constraint penalties, visa ease, experience boosts, explainability strings  
3. **Offline-first judging reliability** — fallback itineraries + keyword experience parsing  
4. **GPT-5.6 product judgment** — cut live booking APIs; keep genome + explainability + What If as the demo spine; Travel Twin as the long-term differentiator  

### What I did *not* do with the LLM

- Let an LLM freely invent destinations without constraints  
- Hide ranking inside a prompt  
- Require paid flights/hotels APIs for the demo  

LLM helps where language helps: **explanations, experience interpretation, itinerary writing**. Hard constraints stay in code.

---

## Key decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Core wedge | Reverse matching, not itinerary-first | Differentiates from typical travel AI tools |
| Ranking | Rules + genome vectors | Explainable, testable, works without LLM |
| LLM placement | Narration / itinerary / NL parse only | Avoids hallucination as the ranking source |
| Geography | Fully global sample set | Stronger demos across passports/hubs |
| Frontend | React (Vite) | Fastest polished web demo |
| Persistence | `localStorage` Twin + saves | Learning loop without auth/DB |
| Deferred | Live Amadeus/Skyscanner booking | Vision yes; not required for a credible demo |

---

