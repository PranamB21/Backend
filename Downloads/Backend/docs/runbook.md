# Local demo runbook

## Application does not start

1. Confirm Python is 3.11 or newer: `python --version`.
2. Activate the environment: `source .venv/bin/activate`.
3. Reinstall dependencies: `make install`.
4. Check `.env` values against `.env.example`; do not paste secrets into logs or bug reports.
5. Run `make check` to separate source errors from Uvicorn startup issues.

## Migration fails

1. Stop the API so no process is writing to the local database.
2. Run `alembic current` and `alembic history`.
3. Read the failed revision's `upgrade()` and `downgrade()`; never apply generated migrations without review.
4. For synthetic demo data, reset using the procedure below. Preserve the database instead if it contains anything that cannot be regenerated.

## Local database is corrupt or disposable data must be reset

This reset is safe only for synthetic, reproducible hackathon data.

```bash
rm -f hackathon.db
alembic upgrade head
```

Do not use this procedure once the database contains important or real-world data. Create and test a backup/restore procedure first.

## Health endpoint reports database unavailable

1. Call `curl -i http://127.0.0.1:8000/api/v1/health` and save the `X-Request-ID`.
2. Find the JSON log with the same request ID.
3. Confirm `BACKEND_DATABASE_URL` points to a writable location.
4. Run `alembic current` to verify database access.
5. Restart the API after correcting the local file or configuration.

## Frontend receives a cross-origin error

Add the frontend's exact origin to the comma-separated `BACKEND_CORS_ORIGINS` value and restart the API. Keep the list explicit; do not use a wildcard when authorization or sensitive data is added.

## Before a judging demo

```bash
make check
alembic upgrade head
curl -f http://127.0.0.1:8000/api/v1/health
```

Use only synthetic data and verify the full user flow after the problem-specific endpoints are added.
