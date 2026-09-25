# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application based on the supplied project document. It provides:

- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image upload
- Gemini-powered recommendation generation
- Mock platform/catalog links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO
- Registration/login with JWT cookies
- Recommendation history
- SQLite persistence
- AI fallback recommendations when Gemini is unavailable

## Important implementation note

The supplied document asks for Gemini 1.5 Flash Pro and third-party platform sourcing, but it also explicitly allows mock API/simulated sourcing. This implementation keeps platform sourcing deterministic and demo-safe, while Gemini is configurable through `GEMINI_MODEL`.

For a new Gemini API key, the default model is `gemini-2.5-flash`. If your account still exposes another supported model, set `GEMINI_MODEL` in `.env`.

## Quick start

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
uvicorn app.main:app --reload
```

## Gemini setup

1. Put your Gemini API key in `.env` as `GEMINI_API_KEY=...`.
2. Keep `GEMINI_MODEL=gemini-2.5-flash` unless your account requires a different supported model.
3. Restart Uvicorn after editing `.env`.

The app still works without a Gemini key using deterministic fallback recommendations, which is useful for classroom demos and UI testing.

## Project structure

```text
PocketSmart-AI/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   ├── ai/
│   │   ├── gemini_service.py
│   │   └── prompts.py
│   ├── services/
│   │   ├── catalog.py
│   │   └── planners.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── home_planner.html
│   │   ├── party_planner.html
│   │   ├── jewelry_planner.html
│   │   ├── recommendations.html
│   │   └── history.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── .env.example
├── requirements.txt
└── README.md
```

## Test flow

1. Register a user.
2. Log in.
3. Try Home Planner with a budget such as 30000.
4. Try Party Planner with 20 guests and a budget such as 15000.
5. Try Jewelry Planner with a budget such as 5000.
6. Upload a JPG/PNG outfit image and submit Jewelry Planner.
7. Open History and Dashboard.
8. For API-level checks, visit http://127.0.0.1:8000/docs.

## API routes

- `POST /register`
- `POST /login`
- `GET /logout`
- `POST /token`
- `GET /session-info`
- `GET /session-data`
- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `GET /recommendations-details/{recommendation_id}`
- `GET /history`
- `GET /startup`
- `GET /health`
