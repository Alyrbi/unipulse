# ADR-01: Modular Monolith vs. Microservices

- **Status:** Accepted
- **Area:** Core system topology

## Context
UniPulse must support 1,000 peak concurrent users with p95 latency under 200 ms, and it is built by a 4-person student team within one semester. Microservices add network hops, distributed transactions and multi-container deployment work.

## Options considered
1. Separate microservices (auth, posts, moderation, AI), each with its own deployment.
2. One FastAPI application split into modules with strict router -> service -> repository boundaries (modular monolith).

## Decision
Option 2. Auth, Posts, Moderation and AI are separate Python modules inside one FastAPI process and share one PostgreSQL database.

## Consequences
- **Positive:** in-process calls (no network latency between modules), normal database transactions instead of distributed ones, one command to run and test everything.
- **Negative:** nothing technically stops one module from reaching into another's internals; code review must enforce the boundaries. Scaling is per whole app, not per module.
