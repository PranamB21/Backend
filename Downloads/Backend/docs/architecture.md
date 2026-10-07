# Architecture decisions

## Current constraints

- One developer is preparing a healthcare hackathon demo.
- The exact problem statement and AI requirement are not known yet.
- The application runs locally, with low request volume and a small dataset.
- The source and sensitivity of future healthcare data are unknown, so initial data must be synthetic.

## Modular monolith

A single deployable application keeps local startup, debugging, and data ownership simple. Modules still have explicit responsibilities, but networked services would add failure modes and deployment work without a current scaling or team boundary. Revisit this only if independently deployed components or separate owning teams become real requirements.

## FastAPI and synchronous request handling

Python aligns with likely AI libraries, while FastAPI supplies boundary validation and an explicit OpenAPI contract. Synchronous SQLAlchemy matches SQLite and the expected low concurrency. Revisit asynchronous I/O if measured external-call or database wait time becomes a bottleneck.

## SQLite and Alembic

SQLite requires no local service and is enough for a small single-process demo. Alembic makes every schema change explicit and reversible. Move to PostgreSQL if the demo needs concurrent writers, database-specific features, or remote deployment; test migration behavior rather than assuming SQLite behavior transfers unchanged.

## No domain schema yet

A generic patient, diagnosis, or medical-record table would encode unsupported assumptions and could be mistaken for a safe clinical data model. Domain tables, constraints, indexes, retention, and audit behavior will be derived from the actual user flow and data source.

## No authentication or AI integration yet

A local-only health check has no protected operation. Authentication, authorization, model providers, retries, circuit breakers, and background work are omitted until concrete endpoints need them. If the application becomes reachable by other users, access control and abuse protection must be designed before exposing sensitive operations.

## Request lifecycle

1. Request middleware validates or creates a request ID.
2. FastAPI validates all path, query, header, and body inputs declared by the route.
3. A route calls one use-case service.
4. The service owns business rules and the transaction boundary.
5. A repository performs parameterized SQLAlchemy queries.
6. Pydantic validates the response contract.
7. Middleware logs method, path, status, duration, and request ID without logging bodies.

Expected failures become typed `ApplicationError` responses. Unexpected failures are logged and become a generic response without internal details.
