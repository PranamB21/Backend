# Backend Engineering Standards

A rulebook defining what separates high-quality, human-grade backend engineering from generic AI-generated output. Every rule here exists to force **justification tied to actual system constraints** — never applied as cargo-cult "best practice."

---

## 1. Architecture & System Design

1. **Derive structure from constraints, not templates.** Before writing a single file, state expected scale (requests/sec, data volume, team size, deployment target). Design decisions (monolith vs. services, sync vs. async, SQL vs. NoSQL) must trace back to one of these constraints — never default to "what's commonly used."
2. **No speculative abstraction.** Don't add plugin systems, generic interfaces, or config flags for scenarios not in the current requirements. Add the seam only when a second concrete use case exists.
3. **Explicit boundaries.** Every module/service must have one clearly stated responsibility and a documented contract (inputs, outputs, side effects, failure modes). No god-objects, no "utils" dumping grounds.
4. **Data flow is directional and traceable.** A request's path through the system (API → service → repository → DB) should be followable in a straight line without circular dependencies or hidden side-channel mutations.
5. **State is owned by exactly one component.** Never let two services independently write to the same table/resource without a defined reconciliation strategy.

## 2. Error Handling & Resilience

6. **Every I/O call (DB, network, filesystem) must have an explicit failure path.** No bare `try/except: pass`, no silently swallowed exceptions.
7. **Distinguish expected vs. unexpected failures.** Expected (validation errors, not-found, conflict) → typed exceptions/result types returned to caller. Unexpected (DB down, OOM) → logged, alerted, converted to safe generic responses — never leaked internals.
8. **Idempotency on all mutating endpoints that can be retried** (payments, order creation, etc.) — via idempotency keys or natural uniqueness constraints.
9. **Timeouts and retries with backoff on every external call.** No unbounded waits. Retries must be capped and jittered to avoid thundering herd.
10. **Graceful degradation over hard failure** where business-acceptable (e.g., serve cached/stale data if a downstream service is down, rather than 500ing the whole request).
11. **Circuit breakers for unreliable dependencies** once a service is called by more than one critical path.

## 3. Security (non-negotiable, not best-effort)

12. **All input validated at the boundary** — type, length, format, business-rule constraints — before it touches business logic. Never trust client input, including headers and query params.
13. **Parameterized queries only. No string-built SQL, ever** — regardless of "it's just an internal tool."
14. **AuthN and AuthZ are separate, explicit layers** — not scattered `if user.role == 'admin'` checks buried in business logic. Centralize permission checks.
15. **Secrets never hardcoded, never logged.** Pulled from env/secret manager only.
16. **Least privilege everywhere** — DB users, service accounts, API keys scoped to only what that component needs.
17. **Rate limiting and abuse protection on public-facing endpoints by default**, not bolted on later.
18. **No sensitive data in error responses** (stack traces, SQL errors, internal paths) returned to the client.

## 4. Data Layer

19. **Schema reflects actual domain constraints** — foreign keys, unique constraints, NOT NULL where appropriate — enforced at the DB level, not just application level.
20. **Migrations are explicit, reversible, and reviewed** — never auto-generated schema changes applied blind.
21. **No N+1 queries.** Batch or join; this is checked explicitly, not left to "it'll probably be fine."
22. **Transactions wrap every multi-step write** that must be atomic. No partial-write states left possible.
23. **Indexes justified by actual query patterns**, not added speculatively or omitted entirely.

## 5. API Design

24. **Consistent, predictable conventions** across all endpoints — naming, pagination, error shape, versioning strategy — decided once, documented, applied everywhere. Not decided fresh per endpoint.
25. **Backward compatibility is a constraint, not an afterthought.** Breaking changes require versioning, not silent mutation of existing contracts.
26. **Responses are explicit contracts** (schema-validated, e.g. via Pydantic/Zod) — no ad-hoc dict/object returns that can silently change shape.

## 6. Code Quality

27. **Names describe domain meaning, not mechanism.** `calculate_shipping_cost()` not `process_data()`.
28. **One voice across the codebase.** Enforce via linter + formatter configs committed to the repo, not left to convention.
29. **Functions do one thing; files have one reason to change** (single responsibility, enforced, not aspirational).
30. **No dead code, no commented-out blocks, no unused imports/config** left "just in case."
31. **Comments explain *why*, not *what*.** Code should be self-explanatory for the "what"; reserve comments for non-obvious business reasoning or tradeoffs.

## 7. Testing

32. **Tests encode intent and edge cases that matter to the business**, not just line coverage. If a bug bit someone in production, there's a regression test for it.
33. **Every error path has a test**, not just the happy path.
34. **Integration tests cover the real I/O boundaries** (DB, external API) via fakes/containers — not everything mocked into meaninglessness.
35. **Flaky tests are fixed or deleted immediately**, never left "quarantined" indefinitely.

## 8. Observability

36. **Structured logging from day one** — JSON logs with request IDs, not `print()` statements.
37. **Every request traceable end-to-end** via correlation/trace IDs across services.
38. **Metrics on the things that actually matter**: latency percentiles (not just averages), error rates, saturation — not vanity metrics.
39. **Alerting tied to user-facing symptoms**, not just infrastructure noise (alert on "checkout failing," not "CPU at 80%" in isolation).

## 9. Performance

40. **Measure before optimizing.** No premature optimization; but also no ignoring obvious O(n²) patterns or synchronous blocking calls on hot paths.
41. **Caching has an explicit invalidation strategy** defined at the time it's added — never "we'll figure out invalidation later."

## 10. Documentation & Operability

42. **README documents how to run, test, and deploy** — not just what the project is.
43. **Every non-obvious architectural decision has a short rationale recorded** (ADR-style) — so future readers (human or AI) understand *why*, not just *what*.
44. **Runbook exists for known failure modes** before shipping to production, not written retroactively after the first incident.

---

## The Meta-Rule

Every rule above requires justification tied to the actual system's constraints — never applied as cargo-cult "best practice." The single biggest gap between strong human backend engineering and generic AI output: humans reason backward from consequences they've actually lived through; AI pattern-matches forward from training examples unless forced to justify each choice against the specific constraints of the system it's building.
