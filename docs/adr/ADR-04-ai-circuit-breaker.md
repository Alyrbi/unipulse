# ADR-04: Circuit Breaker with Heuristic Fallback for the AI Feature

- **Status:** Accepted
- **Area:** PulseDigest AI (FR-AI-01, NFR-RESIL-01)

## Context
PulseDigest asks an external LLM to summarise an announcement and extract event date/location. External LLMs can be slow (3–10 s) or hit quota limits. Publishing a post must never depend on the AI being up.

## Options considered
1. Call the LLM synchronously while creating the post.
2. Separate preview call with a 3.0 s timeout, a circuit breaker, and a local rule-based fallback.

## Decision
Option 2. `POST /api/posts/ai/preview` calls the LLM with a 3.0 s timeout. On timeout or error the breaker opens and the endpoint returns `200 OK` with a rule-based summary and `is_fallback: true`. The author must accept the suggestion before it is saved ("AI drafts, human verifies").

## Consequences
- **Positive:** publishing never fails because of the AI provider; users always get an answer within about 3 s.
- **Negative:** fallback summaries are simpler (sentence picking, not rewriting). The UI must show clearly when a summary is a fallback.
