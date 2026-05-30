# Users API

A typical CRUD REST API for managing users. It's intentionally small and
conventional — the point isn't the API itself, it's a practice project for:

- **Deploying to the cloud** (containerized with Docker).
- **Connecting to a managed/cloud database** (PostgreSQL).
- **Wiring it up to a React frontend** that consumes the API.

Built with [FastAPI](https://fastapi.tiangolo.com/) + [PostgreSQL](https://www.postgresql.org/),
using async [psycopg](https://www.psycopg.org/psycopg3/) with a connection pool.

## Tech stack

- Python 3.13 / FastAPI
- PostgreSQL 16
- psycopg 3 (async + connection pool)
- Pydantic v2 for validation
- Docker / docker-compose

## API endpoints

| Method   | Path               | Description                  |
| -------- | ------------------ | ---------------------------- |
| `GET`    | `/health`          | Liveness + DB check          |
| `GET`    | `/users`           | List users (`limit`, `offset`) |
| `GET`    | `/users/{id}`      | Get a single user            |
| `POST`   | `/users`           | Create a user                |
| `PATCH`  | `/users/{id}`      | Partially update a user      |
| `DELETE` | `/users/{id}`      | Delete a user                |

Interactive docs are available at `/docs` (Swagger UI) once the app is running.

### User model

```json
{
  "id": 1,
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "age": 36,
  "created": "2026-05-30T12:00:00Z"
}
```

`name` and `email` are required on create; `email` is unique (a duplicate
returns `409`). `age` is optional and must be `>= 0`.

## Running locally with Docker

1. Copy the example env file and set your own values:

   ```bash
   cp .env.example .env
   ```

2. Start the database and API:

   ```bash
   docker compose up --build
   ```

The schema in `initdb/01_schema.sql` is applied automatically the first time
the Postgres volume is created. The API will be available at
`http://localhost:8000`.

## Running the API without Docker

Requires a reachable PostgreSQL instance.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL="postgresql://user:password@host:5432/dbname"
uvicorn main:app --reload
```

The `DATABASE_URL` environment variable is required — the app refuses to start
without it.

## Environment variables

| Variable            | Used by         | Description                                  |
| ------------------- | --------------- | -------------------------------------------- |
| `DATABASE_URL`      | API             | Full Postgres connection string              |
| `POSTGRES_USER`     | docker-compose  | DB user (composes into `DATABASE_URL`)       |
| `POSTGRES_PASSWORD` | docker-compose  | DB password                                  |
| `POSTGRES_DB`       | docker-compose  | DB name                                      |

## Cloud deployment notes

When deploying to a cloud provider:

- Point `DATABASE_URL` at your managed database (e.g. Cloud SQL, RDS, Neon,
  Supabase). Most managed Postgres providers require SSL — append
  `?sslmode=require` to the connection string if so.
- Build and push the image from the included `Dockerfile`, then run it on your
  platform of choice (Cloud Run, ECS, Fly.io, Railway, etc.).
- Apply `initdb/01_schema.sql` to the cloud database once (the
  `docker-entrypoint-initdb.d` hook only runs for the local Postgres container).

## Connecting a React frontend

To call this API from a React app running on a different origin, you'll need to
enable CORS in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your React dev server / prod URL
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then from React, fetch against the API base URL, for example:

```js
const res = await fetch(`${API_URL}/users`);
const users = await res.json();
```
