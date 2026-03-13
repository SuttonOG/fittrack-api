# FitTrack API — Workout & Fitness Analytics

A RESTful API for tracking exercises, workout plans, and logged sessions, with analytical endpoints for progress tracking, personal records, and training volume trends. Includes a frontend dashboard and strength benchmark comparison powered by external data.

Built with **FastAPI**, **SQLAlchemy**, and **SQLite** for the COMP3011 Web Services & Web Data coursework.

**Live deployment:** https://fittrack-api-kwno.onrender.com

---

## Features

- **User authentication** — JWT-based register/login flow with bcrypt password hashing
- **Exercise catalogue** — full CRUD with filtering by muscle group and difficulty
- **Workout plans** — user-scoped CRUD for planning training sessions
- **Workout logs** — log sets, reps, and weight per exercise per session
- **Analytics endpoints** — personal records, weekly/monthly volume trends, muscle-group distribution, workout streaks
- **Strength benchmarks** — compare your lifts against population standards (data from ExRx.net and Strength Level)
- **Frontend dashboard** — interactive single-page UI with Chart.js analytics and benchmark comparison
- **Auto-generated docs** — interactive Swagger UI at `/docs`
- **38 passing tests** — comprehensive test suite with pytest

---

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Framework | FastAPI | Auto-generated OpenAPI docs, async support, Pydantic validation |
| ORM | SQLAlchemy 2.0 | Mature, flexible, supports multiple DB backends |
| Database | SQLite | Zero-config for local dev; swappable to PostgreSQL in production |
| Auth | python-jose + passlib | Industry-standard JWT + bcrypt hashing |
| Testing | pytest + httpx | Fast, fixture-based testing with TestClient |
| Frontend | HTML/CSS/JS + Chart.js | Single-file dashboard with interactive analytics visualisations |
| Deployment | Render | Native ASGI support, automatic Git-based deploys |

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/SuttonOG/fittrack-api.git
cd fittrack-api
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Seed the Database

```bash
python -m app.seed
```

### Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Frontend dashboard: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

### Run Tests

```bash
pytest -v
```

---

## API Endpoints Overview

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Obtain JWT token |
| GET | `/auth/me` | Get current user profile |

### Exercises
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/exercises/` | Add an exercise |
| GET | `/exercises/` | List exercises (filter by muscle_group, difficulty) |
| GET | `/exercises/{id}` | Get exercise by ID |
| PUT | `/exercises/{id}` | Update exercise |
| DELETE | `/exercises/{id}` | Delete exercise |

### Workouts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workouts/` | Create a workout plan |
| GET | `/workouts/` | List your workouts |
| GET | `/workouts/{id}` | Get workout by ID |
| PUT | `/workouts/{id}` | Update workout |
| DELETE | `/workouts/{id}` | Delete workout |

### Workout Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/logs/` | Log an exercise entry |
| GET | `/logs/` | List your logs (filter by workout_id, exercise_id) |
| GET | `/logs/{id}` | Get log entry by ID |
| PUT | `/logs/{id}` | Update log entry |
| DELETE | `/logs/{id}` | Delete log entry |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/personal-records` | Best lift per exercise |
| GET | `/analytics/volume-trends?period=weekly` | Training volume over time |
| GET | `/analytics/muscle-group-distribution` | Sets per muscle group (pie chart data) |
| GET | `/analytics/streak` | Current and longest workout streak |
| GET | `/analytics/benchmarks?gender=male&bodyweight_kg=80` | Compare PRs against population strength standards |

---

## Data Sources

The strength benchmarks dataset was compiled from publicly available strength standards:

- **ExRx.net** — https://exrx.net/Testing/WeightLifting/StrengthStandards
- **Strength Level** — https://strengthlevel.com/strength-standards

See [`data/README.md`](./data/README.md) for full citation details.

---

## API Documentation

Full API documentation is auto-generated via FastAPI's OpenAPI integration and available at `/docs` (Swagger UI) when the server is running.

A PDF export of the documentation is included in this repository: [`api-docs.pdf`](./api-docs.pdf)

---

## Project Structure

```
fittrack-api/
├── main.py                  # FastAPI app entry point
├── requirements.txt
├── .python-version          # Python 3.11 pin for Render
├── api-docs.pdf             # API documentation PDF
├── data/
│   ├── README.md            # Data source citations
│   └── strength_benchmarks.csv  # Benchmark dataset (72 rows)
├── static/
│   └── index.html           # Frontend dashboard
├── app/
│   ├── config.py            # Settings & environment config
│   ├── database.py          # SQLAlchemy engine & session
│   ├── seed.py              # Exercise + benchmark data import
│   ├── auth/
│   │   └── jwt.py           # JWT creation, verification, dependencies
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── exercise.py
│   │   ├── workout.py
│   │   ├── workout_log.py
│   │   └── benchmark.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── exercise.py
│   │   ├── workout.py
│   │   └── workout_log.py
│   └── routers/             # API route handlers
│       ├── auth.py
│       ├── exercises.py
│       ├── workouts.py
│       ├── workout_logs.py
│       └── analytics.py
└── tests/                   # pytest test suite (38 tests)
    ├── conftest.py
    ├── test_auth.py
    ├── test_exercises.py
    ├── test_workouts.py
    ├── test_workout_logs.py
    ├── test_analytics.py
    └── test_benchmarks.py
```

---

## Licence

This project was developed for academic purposes as part of COMP3011 at the University of Leeds.
