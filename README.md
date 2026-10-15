# UniPulse: Campus Social Network

UniPulse is an integrated campus social and communications platform designed to resolve information fragmentation across student societies, academic departments, and the broader university community. It incorporates role-scoped audience feeds, real-time collaboration with optimistic concurrency control, automated 3-flag moderation triage, and the PulseDigest AI summarizer ("AI drafts, human verifies").

This repository contains the complete deliverables for **AI1220 Assignment 1: Requirements Engineering, System Architecture & Proof of Concept**.

---

## Team

| Member | Role | Owns | GitHub | Student ID |
|---|---|---|---|---|
| Ali Yaroobi | Backend & API Lead | `src/backend/` | [@Alyrbi](https://github.com/Alyrbi) | 25011226 |
| Saidamirkhon Yusupov | Frontend & UI/UX Lead | `src/frontend/` | [@Saidamirhon07](https://github.com/Saidamirhon07) | 25011163 |
| Ahmed Waqqas | Architecture & Integration Lead | `docs/diagrams/`, `docs/adr/`, `ai_service.py` | [@awalawlaqi](https://github.com/awalawlaqi) | 25011081 |
| Rawda Alkhoori | QA, Requirements & DevOps Lead | `tests/`, `.github/`, report | [@rawdajjkk](https://github.com/rawdajjkk) | 25011159 |

---

## Repository Structure

```text
.
├── .github/
│   ├── CODEOWNERS                  # Auto-requests a review from the owner of each area
│   └── workflows/ci.yml            # CI: ruff + pytest on every push and pull request
├── docs/
│   ├── Assignment_01_Report.pdf    # Official submission report (single PDF)
│   ├── Assignment_01_Report.docx   # Editable source of the report
│   ├── adr/                        # Architecture Decision Records ADR-01 … ADR-04
│   ├── diagrams/                   # Editable draw.io sources (one file per diagram)
│   │   ├── System Context Diagram.drawio                       # C4 Level 1
│   │   ├── Container Diagram.drawio                            # C4 Level 2
│   │   ├── Backend Component Diagram.drawio                    # C4 Level 3
│   │   ├── UML Sequence Diagram - Collaborative Drafting.drawio
│   │   ├── Stakeholder Power vs. Interest Grid.drawio
│   │   ├── Requirements Traceability Flow.drawio
│   │   ├── Data Model ERD.drawio
│   │   ├── unipulse_all_diagrams.drawio                        # All diagrams as tabs in one file
│   │   ├── make_sequence.py        # Regenerates the sequence diagram (.drawio + PNG)
│   │   └── exports/                # PNG exports used in the report
│   └── screenshots/                # PoC running (Swagger UI, server log)
├── src/
│   ├── backend/                    # Python FastAPI backend application
│   │   ├── config.py               # Pydantic BaseSettings and environment loading
│   │   ├── models.py               # Domain models and enums
│   │   ├── schemas.py              # Pydantic request/response contracts
│   │   ├── repository.py           # In-memory repository with query scoping
│   │   ├── services/               # Business logic
│   │   │   ├── post_service.py     # Post publishing and audience rules
│   │   │   └── ai_service.py       # PulseDigest summarizer & circuit breaker
│   │   ├── routers/                # REST API routers
│   │   │   ├── health.py           # Liveness and readiness probes
│   │   │   └── posts.py            # Post endpoints and AI preview
│   │   └── main.py                 # FastAPI ASGI entry point
│   └── frontend/                   # Browser UI (HTML, CSS, vanilla JS)
│       ├── index.html
│       ├── style.css
│       └── app.js
├── tests/                          # Automated test suite (22 tests)
│   ├── conftest.py
│   ├── test_unit_models.py
│   ├── test_poc_contract.py
│   └── test_bva_equivalence.py
├── pyproject.toml                  # Dependencies, pytest and Ruff configuration
├── uv.lock                         # Dependency lockfile
├── .env.example                    # Environment template (copy to .env, never commit .env)
├── .gitignore
├── LICENSE
└── README.md
```

---

## Quickstart & Installation

### 1. Prerequisites
- Python 3.11 or newer
- `uv` (recommended) or standard Python `venv` + `pip`

### 2. Environment Setup
```bash
# Clone the repository and navigate into the workspace
git clone <repository_url>
cd unipulse

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install the app AND the dev tools (pytest, httpx, ruff)
pip install -e ".[dev]"
# Alternatively with uv: uv pip install -e ".[dev]"
```

### 3. Running the Application
```bash
# Launch FastAPI backend with reload
python -m uvicorn backend.main:app --app-dir src --host 127.0.0.1 --port 8000 --reload
```
Once launched, open your web browser to:
- **Application Frontend:** `http://127.0.0.1:8000/`
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`

---

## Verification & Testing

### Running the Test Suite
`pytest` is preconfigured via `pyproject.toml` with `pythonpath = ["src"]`, enabling direct execution:
```bash
pytest
```
The test suite executes 22 automated tests covering:
- Service and model unit tests (boundary rules, invariants, standardized enums)
- REST interface contract verification (`GET /api/posts`, `POST /api/posts`, `GET /api/posts/{id}`, `POST /api/posts/ai/preview`)
- Server-side audience scoping authorization (HTTP 403 Forbidden on faculty posts for students, HTTP 200 OK for faculty)
- Bearer token authentication and mock session header validation (`Authorization`, `X-Mock-Role`, HTTP 401 on invalid token)
- Nullable community space handling (`community_id: null` contract acceptance)
- Boundary Value Analysis (BVA) for character limits (3–120 for titles, 5–5,000 for content)
- Equivalence partitioning for audience tiers (Public, Campus Only, Club Members, Faculty Only)
- Word-boundary regex event extraction (eliminating false positives on words like "team" and "name")
- Isolated AI circuit breaker timeout fallback (>3.0s latency returns `is_fallback: true`)
- Missing record error handling (404 Not Found) and validation errors (422 Unprocessable Entity)

### Code Style & Linter Checks
```bash
ruff check src tests
```
All code complies with PEP 8 and passes Ruff with zero errors and zero warnings.

---

## Proof-of-Concept Simplifications

The PoC implements one vertical slice of the planned architecture (report Section 4.1):

1. **In-memory repository** instead of PostgreSQL. Same `PostRepository` interface, so the audience-scoping rule is identical.
2. **Local heuristic AI** instead of a real LLM. Same response contract (`summary`, `detected_event`, `is_fallback`, ...), no paid API.
3. **Plain HTML/JS** instead of the planned React + rich-text editor.
4. **Polling / refresh after submit** instead of WebSocket live updates.
5. **Mock identity:** the role comes from the `X-Mock-Role` header or a mock bearer token instead of campus SSO.
6. **`POST /api/posts` trusts `author_id` from the request body.** In Assignment 2 the author is taken from the verified token, and 401/403 are returned as defined in the contract.

## Interface Contract Used by the PoC

The browser and backend exchange exactly the JSON defined in report Section 2.4:
`GET /api/posts`, `GET /api/posts/{id}`, `POST /api/posts`, `POST /api/posts/ai/preview`.
The live, machine-readable version is at `http://127.0.0.1:8000/docs` while the server runs.

---

## Three-Minute Demonstration Outline (Oral Defense)

1. **Minute 1: Problem & System Context**
   - Introduce UniPulse and explain campus communication fragmentation across student societies.
   - Walk through C4 Context (Level 1) and Container (Level 2) diagrams, highlighting container boundaries and external systems (SSO, LLM, SMTP).
2. **Minute 2: Core Contract Demonstration & PulseDigest AI**
   - In `http://127.0.0.1:8000/`, fill in announcement details ("ACM Study Jam"), select "Campus Only" audience scope, and trigger "AI Preview".
   - Demonstrate the PulseDigest event extractor, showing location and date rendering, 2-sentence summary, and the "Accept Summary" human-in-the-loop verification checkbox (FR-AI-02).
   - Click "Publish Post" to execute `POST /api/posts` (201 Created) and observe dynamic DOM feed insertion.
3. **Minute 3: Server-Side Authorization & Test Verification**
   - Demonstrate real implementation of authorizations on the server: Switch to the "Student" mock role selector in the header.
   - Try to access a Faculty Only Announcement via `GET /api/posts/{faculty_post_id}` or click "Verify Audience Access" on post `p-103`.
   - Ensure that the endpoint responds with a 403 Forbidden response containing the `FORBIDDEN_AUDIENCE` error code to prove audience privacy is enforced at the backend query layer, and not just in the UI. Switch to "Faculty" to show access succeeds with 200 OK.
   - Conclude by running `pytest` and `ruff check src tests` live in the terminal to demonstrate 22 passing automated tests and clean PEP 8 compliance.

