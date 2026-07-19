# Reverse Travel Planner

**Don't choose a destination. Choose the experience.**

Most travel apps ask *where* you want to go. This one asks *what kind of trip you want* — budget, days, visa friction, weather, pace, vibes — and returns ranked destinations with explainable match scores.

Built for OpenAI Build Week as a working product demo: constraint matching + destination genome + Trip DNA + What If mode + Groq-powered explanations.

## Demo flow

1. Describe your ideal trip (not a city)
2. Get ranked global destinations with % match
3. Open a match → Spotify-style dimension bars + why ✅/❌
4. Drag **What If** sliders → recommendations reshuffle live
5. Optional: generate a Groq LLM explanation

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | React (Vite) |
| Backend | FastAPI |
| Ranking | Rule + feature-vector Destination Genome |
| Explanations | Groq (`llama-3.3-70b-versatile`) with offline fallback |

## Quick start

### 1. Backend

```bash
cd backend
python -m pip install -r requirements.txt
copy .env.example .env
# optional: add GROQ_API_KEY=... to .env
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

Without a Groq key the app still works — recommendations, scores, reasons, budget split, and What If all run locally. Groq only powers richer narrative explanations and experience-query parsing.

## API

- `GET /api/health`
- `GET /api/meta`
- `POST /api/recommend`
- `POST /api/explain`
- `POST /api/experience-search`
- `GET /api/destinations`

## Why this is different

> Other tools answer: “What should I do in Paris?”  
> This answers: “Given who you are and your constraints, where should you go in the first place?”
