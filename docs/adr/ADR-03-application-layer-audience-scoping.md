# ADR-03: Audience Scoping in the Repository Layer vs. PostgreSQL Row Level Security

- **Status:** Accepted
- **Area:** Audience access control (FR-AUD-01, NFR-SEC-01, NFR-PRIV-01)

## Context
Posts have an audience (Public, Campus Only, Club Members, Faculty Only). A student must never receive a Faculty Only post, not even in a raw API response. Hiding it only in the UI is not enough.

## Options considered
1. PostgreSQL Row Level Security (RLS), driven by per-connection session variables.
2. Application-layer scoping: `PostRepository` adds the caller's role and community memberships (taken from the verified token) to every query's `WHERE` clause.

## Decision
Option 2. All post reads go through `PostRepository`; route handlers never query posts directly. Single-post reads that are out of scope return `403 FORBIDDEN_AUDIENCE`.

## Consequences
- **Positive:** the rule is plain Python that we can unit-test without a database (the PoC does this with an in-memory repository); works with connection poolers; no database-specific session state.
- **Negative:** the protection is only as good as our discipline. A new query written outside `PostRepository` could leak data. We reduce this with code review (CODEOWNERS on `repository.py`) and contract tests that assert a student gets 403 on faculty posts. We also need a composite index on `(audience, community_id)` to keep feed queries under 200 ms.
