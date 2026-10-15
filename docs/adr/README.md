# Architecture Decision Records

Each file records one decision: context, options considered, decision, consequences.
These are the same four ADRs as Section 2.7 of the report. If a decision changes,
add a new ADR that supersedes the old one instead of silently editing history.

| ID | Decision | Status |
|----|----------|--------|
| [ADR-01](ADR-01-modular-monolith.md) | Modular monolith instead of microservices | Accepted |
| [ADR-02](ADR-02-optimistic-concurrency.md) | Optimistic concurrency (version numbers) instead of CRDTs for co-drafting | Accepted |
| [ADR-03](ADR-03-application-layer-audience-scoping.md) | Audience scoping in the repository layer instead of PostgreSQL RLS | Accepted |
| [ADR-04](ADR-04-ai-circuit-breaker.md) | AI calls behind a 3.0 s circuit breaker with heuristic fallback | Accepted |
