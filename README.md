# Travel Planner – Backend API

FastAPI backend for the Travel Planner: manage projects and places (Art Institute of Chicago API).

## Setup

1. **Python 3.10+** and a virtual environment:

   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Environment (optional)**

   - `DATABASE_URL` – default `sqlite:///./travel_planner.db`
   - `ARTIC_BASE_URL` – default `https://api.artic.edu/api/v1`
   - `CORS_ORIGINS` – comma-separated origins; default `http://localhost:3000`
   - `ARTIC_CACHE_TTL` – cache Art Institute responses (seconds); default `3600`; `0` = disable
   - `BASIC_AUTH_USER` / `BASIC_AUTH_PASSWORD` – if both set, project/place endpoints require HTTP Basic Auth

## Run

```bash
uvicorn main:app --reload
```

API: `http://localhost:8000`

### Docker (backend + frontend)

From the **repository root** (parent of `backend/`):

```bash
docker compose up --build
```

Backend: `http://localhost:8000`, frontend: `http://localhost:3000`. Database is stored in a Docker volume `backend-data`.  
Health: `http://localhost:8000/`

## API documentation (OpenAPI / Swagger)

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

You can import `openapi.json` into Postman if you want a Postman collection.

## Main endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check (no auth) |
| POST | `/projects` | Create project (optional `place_ids`: Art Institute artwork IDs) |
| GET | `/projects` | List projects (paginated: `skip`, `limit`; filter: `search`, `completed`) |
| GET | `/projects/{id}` | Get project with places |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project (fails if any place is visited) |
| GET | `/projects/{id}/places` | List places (paginated: `skip`, `limit`) |
| POST | `/projects/{id}/places` | Add place (body: `external_id`, optional `notes`) |
| GET | `/projects/{id}/places/{place_id}` | Get place |
| PATCH | `/projects/{id}/places/{place_id}` | Update place (`notes`, `visited`) |

## Example requests

**Create project (no places):**
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Paris 2025", "description": "Week in Paris"}'
```

**Create project with places (Art Institute artwork IDs):**
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Chicago Art", "description": "Museum trip", "place_ids": ["27992", "16568"]}'
```

**Add place to project:**
```bash
curl -X POST http://localhost:8000/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{"external_id": "27992", "notes": "Must see"}'
```

**Mark place as visited:**
```bash
curl -X PATCH http://localhost:8000/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"visited": true}'
```

## Project structure

- `main.py` – App entry, CORS, routers
- `config.py` – Settings
- `database.py` – Engine, session, `get_db`, `init_db`
- `models/` – SQLAlchemy (Project, ProjectPlace)
- `schemas/` – Pydantic request/response + serializers
- `services/` – Art Institute API client
- `controllers/` – Business logic
- `routes/` – API routes (projects, places)
