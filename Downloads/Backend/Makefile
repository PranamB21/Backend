.PHONY: install run migrate lint format test check

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

test:
	pytest

check: lint test
