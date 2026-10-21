# ADR-003: Prevent double booking with a database constraint, not only an application check

- **Status:** Accepted
- **Date:** 2026-10-21
- **Deciders:** Tariq Algadheeb, Abdullah
- **Supersedes:** none
- **Related requirements:** FR-09, FR-10, FR-11, NFR-01
- **Trade-off matrix rows:** T3

## Context
Two students may press *Book* on the same slot at nearly the same moment (SC-10). The AI first draft (Draft 0) checked "is the slot free?" in Python and then inserted the booking. Two requests can both pass the check before either inserts, which creates two bookings. NFR-01 requires 0 double bookings across 100 race-test runs.

## Decision
1. Add a **partial unique index**: `CREATE UNIQUE INDEX one_active_booking_per_slot ON bookings(slot_id) WHERE status = 'active'`. SQLite has supported partial indexes since version 3.8.0.
2. Run `book_slot` inside a transaction started with **`BEGIN IMMEDIATE`**, so the per-student rules (FR-10, FR-11) are checked while holding SQLite's write lock.
3. The service catches `IntegrityError` and returns the "slot was just booked by someone else" message (UC-01 flow 4a).

## Rejected alternative
**Application-level check-then-insert only** (the Draft 0 approach, optionally with a Python `threading.Lock`). Rejected because it is race-prone across requests. A Python lock only protects a single process and silently stops working if the app is ever run with several workers.

## Accepted downside
- **Database-specific behaviour:** correctness depends on SQLite's partial index and write-lock semantics. Moving to Postgres would need an equivalent constraint and a different locking approach, which we would record in a superseding ADR.
- **Error translation code:** the service must turn a low-level `IntegrityError` into a user message. A mistake here could show users a 500 error.
- **Serialised writes:** every booking waits for the write lock (accepted under [ADR-002](ADR-002-sqlite-on-persistent-disk.md)).

## Consequences
- The concurrency test (10 threads × 100 runs) and the integrity query in NFR-01 become part of the M2 suite.
- The domain rule `check_booking()` still validates FR-08, FR-10 and FR-11 for clear error messages. The index is the final safety net for FR-09.
