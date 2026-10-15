# ADR-02: Optimistic Concurrency Control vs. CRDTs for Collaborative Drafting

- **Status:** Accepted
- **Area:** Real-time collaborative editing (FR-COL-01)

## Context
Club executives co-draft announcements over WebSockets. Two people editing at the same time must never silently overwrite each other.

## Options considered
1. Pessimistic locking (one editor holds a lock on the draft).
2. CRDTs (e.g. Yjs) that merge every keystroke automatically.
3. Optimistic concurrency control (OCC): every draft has an integer `version`; every `draft.update` carries the `base_version` it was based on.

## Decision
Option 3. The save is `UPDATE drafts SET ..., version = version + 1 WHERE id = :id AND version = :base_version`. If 0 rows change, someone else saved first, and the server answers `VERSION_OUTDATED {current_version}`. See the sequence diagram `docs/diagrams/UML Sequence Diagram - Collaborative Drafting.drawio`.

## Consequences
- **Positive:** no locks held, simple to implement and test, the database guarantees correctness.
- **Negative:** when two people really edit at the same moment, the second one has to look at the newer version and re-apply their change. Acceptable for short announcements; would not be acceptable for long documents (then CRDTs would be the better choice).
