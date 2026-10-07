# Healthcare Hackathon Backend

A small FastAPI foundation for a local healthcare hackathon prototype. It deliberately contains no invented patient model or AI integration; those should follow the actual problem statement.

> **Prototype boundary:** use synthetic data only for now. This project does not claim HIPAA compliance and must not receive real protected health information.

## What is included

- Versioned FastAPI routes and interactive OpenAPI documentation
- SQLite connectivity with SQLAlchemy and explicit Alembic migrations
- Boundary validation and one consistent JSON error contract
- Structured JSON request logs with request IDs
- Explicit local cross-origin configuration
- Integration tests for readiness, failure paths, request IDs, and cross-origin behavior

## Requirements

- Python 3.11 or newer

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
make install
cp .env.example .env
```

## Run

```bash
make migrate
make run
```

Open:

- API documentation: <http://127.0.0.1:8000/docs>
- Health/readiness endpoint: <http://127.0.0.1:8000/api/v1/health>

Example:

```bash
curl -i -H 'X-Request-ID: demo-1' http://127.0.0.1:8000/api/v1/health
```

Expected body:

```json
{"status":"ok","database":"ok"}
```

## Develop and test

```bash
make format
make check
```

`make check` runs Ruff and the full pytest suite. Tests use isolated temporary SQLite databases and do not modify `hackathon.db`.

## Configuration

Settings are read from environment variables or `.env`. All names use the `BACKEND_` prefix.

| Setting | Local default | Purpose |
| --- | --- | --- |
| `BACKEND_DATABASE_URL` | `sqlite:///./hackathon.db` | SQLAlchemy database connection |
| `BACKEND_LOG_LEVEL` | `INFO` | Python log level |
| `BACKEND_CORS_ORIGINS` | Local ports 3000 and 5173 | Comma-separated allowed frontend origins |
| `BACKEND_ENVIRONMENT` | `local` | Runtime label |

Never commit `.env`; `.env.example` contains only safe defaults.

## Adding the first domain feature

Wait for the problem statement, then define the real entity and flow. Keep the request path directional:

```text
API route -> service -> repository -> database
```

- **API route:** validates HTTP input and serializes the response.
- **Service:** owns the use case and transaction boundary.
- **Repository:** performs domain-specific database queries.
- **Database:** enforces actual nullability, uniqueness, and relationship constraints.

Add a model import to Alembic metadata, generate a revision, review both `upgrade()` and `downgrade()`, and only then apply it:

```bash
alembic revision --autogenerate -m "add concrete domain model"
alembic upgrade head
alembic downgrade -1  # verify reversibility before relying on the migration
alembic upgrade head
```

Do not add generic base repositories, placeholder patient tables, or AI provider interfaces before a second concrete use case requires a reusable seam.

## Error contract

Expected and unexpected errors have the same outer shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "request_id": "demo-1",
    "details": []
  }
}
```

Unexpected failures are logged with their request ID while the client receives no stack trace, SQL error, or local path.

## More documentation

- [Architecture decisions](docs/architecture.md)
- [Local demo runbook](docs/runbook.md)
- [Backend engineering rules](BACKEND_STANDARDS.md)
