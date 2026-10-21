# Traceability Matrix

Each requirement links forward to its stories, use case, scenarios, architecture element, ADR, the planned test and code module, and the matching risk. Every link in this file is checked by `python tools/check_m1.py`, which fails on broken links, orphan requirements or orphan scenarios.

- **Tests and code modules** are *planned* names for M2. When the code exists, replace "planned" with the commit hash that adds the test.
- **Architecture elements** refer to Option A in [ARCHITECTURE_OPTIONS.md](architecture/ARCHITECTURE_OPTIONS.md#option-a-server-rendered-modular-monolith--sqlite-chosen).

## Functional requirements

| Req | Stories | Use case | Scenarios | Architecture element (Option A) | ADR | Planned test | Planned module | Risk |
|---|---|---|---|---|---|---|---|---|
| [FR-01](REQUIREMENTS.md#fr-01-log-in-and-out) | US-01 | UC-05 | SC-16 | web: auth (session cookie, bcrypt) | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | `tests/web/test_auth.py::test_sc16_wrong_password_sets_no_session` | `app/web/auth.py` | R4 |
| [FR-02](REQUIREMENTS.md#fr-02-role-based-access) | US-01 | UC-05 | SC-13 | web: role dependency | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | `tests/web/test_access_matrix.py::test_sc13_student_cannot_post_blocks` | `app/web/deps.py` | — |
| [FR-03](REQUIREMENTS.md#fr-03-publish-a-block) | US-02 | UC-03 | SC-03 | domain: `validate_block`; services: `publish_block` | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | `tests/domain/test_blocks.py::test_sc03_slot_length_25_rejected` | `app/domain/blocks.py` | R3 |
| [FR-04](REQUIREMENTS.md#fr-04-generate-slots) | US-02 | UC-03 | SC-01, SC-02 | domain: `generate_slots` | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | `tests/domain/test_slots.py::test_sc01_four_slots`, `::test_sc02_leftover_discarded` | `app/domain/slots.py` | R3 |
| [FR-05](REQUIREMENTS.md#fr-05-cancel-a-block) | US-03 | UC-04 | SC-14 | services: `cancel_block` → repositories | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | `tests/services/test_cancel_block.py::test_sc14_bookings_cancelled_by_instructor` | `app/services/blocks.py` | — |
| [FR-06](REQUIREMENTS.md#fr-06-view-open-slots) | US-04 | UC-01 | SC-15 | web: slots router; repositories: `open_slots` | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | `tests/web/test_slots_page.py::test_sc15_shows_riyadh_time` | `app/web/slots.py` | R6 |
| [FR-07](REQUIREMENTS.md#fr-07-book-a-slot) | US-05 | UC-01 | SC-04 | services: `book_slot` | [ADR-003](adr/ADR-003-db-enforced-double-booking-prevention.md) | `tests/services/test_book_slot.py::test_sc04_booking_created` | `app/services/bookings.py` | R1 |
| [FR-08](REQUIREMENTS.md#fr-08-booking-window) | US-05 | UC-01 | SC-04, SC-05, SC-06 | domain: `check_booking` | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | `tests/domain/test_booking_rules.py::test_sc05_lead_59_rejected`, `::test_sc06_max_ahead_boundary` | `app/domain/booking_rules.py` | R3 |
| [FR-09](REQUIREMENTS.md#fr-09-one-student-per-slot) | US-05 | UC-01 | SC-10 | DB: partial unique index; services | [ADR-003](adr/ADR-003-db-enforced-double-booking-prevention.md), [ADR-002](adr/ADR-002-sqlite-on-persistent-disk.md) | `tests/integration/test_race.py::test_sc10_exactly_one_winner` | `app/repositories/bookings.py` | R1 |
| [FR-10](REQUIREMENTS.md#fr-10-per-instructor-limit) | US-06 | UC-01 | SC-07 | domain: `check_booking`; services: `BEGIN IMMEDIATE` | [ADR-003](adr/ADR-003-db-enforced-double-booking-prevention.md) | `tests/domain/test_booking_rules.py::test_sc07_third_booking_rejected` | `app/domain/booking_rules.py` | R1 |
| [FR-11](REQUIREMENTS.md#fr-11-no-overlapping-bookings) | US-05 | UC-01 | SC-08, SC-09 | domain: `overlaps` | [ADR-003](adr/ADR-003-db-enforced-double-booking-prevention.md), [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | `tests/domain/test_booking_rules.py::test_sc08_touching_allowed`, `::test_sc09_overlap_rejected` | `app/domain/booking_rules.py` | R1 |
| [FR-12](REQUIREMENTS.md#fr-12-student-cancels-a-booking) | US-07 | UC-02 | SC-11, SC-12 | domain: `can_cancel` | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | `tests/domain/test_cancel_rules.py::test_sc11_exactly_120_allowed`, `::test_sc12_119_rejected` | `app/domain/cancel_rules.py` | R3 |
| [FR-13](REQUIREMENTS.md#fr-13-my-bookings) | US-08 | UC-02 | SC-14 | web: my-bookings router | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | `tests/web/test_my_bookings.py::test_sc14_status_shown` | `app/web/me.py` | — |
| [FR-14](REQUIREMENTS.md#fr-14-instructor-schedule) | US-09 | UC-03 | SC-14 | web: schedule router | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | `tests/web/test_schedule.py::test_sc14_schedule_shows_cancelled` | `app/web/schedule.py` | — |

## Non-functional requirements

| Req | Scenarios | Architecture element (Option A) | ADR | Trade-off row | Planned verification | Risk |
|---|---|---|---|---|---|---|
| [NFR-01](REQUIREMENTS.md#nfr-01-booking-integrity-under-concurrency) | SC-10 | DB index + `BEGIN IMMEDIATE` in services | [ADR-003](adr/ADR-003-db-enforced-double-booking-prevention.md), [ADR-002](adr/ADR-002-sqlite-on-persistent-disk.md) | [T3](architecture/TRADEOFF_MATRIX.md) | `tests/integration/test_race.py` (10 threads × 100 runs) + integrity query | R1 |
| [NFR-02](REQUIREMENTS.md#nfr-02-access-control) | SC-13 | web: role dependency on every route | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | [T5](architecture/TRADEOFF_MATRIX.md) | `tests/web/test_access_matrix.py` (all 10 endpoints × 3 user types) | — |
| [NFR-03](REQUIREMENTS.md#nfr-03-credential-and-secret-protection) | SC-16 | web: auth; CI gitleaks | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | [T5](architecture/TRADEOFF_MATRIX.md) | `tests/web/test_auth.py::test_password_stored_as_bcrypt`, cookie-flag test, gitleaks CI job | R4 |
| [NFR-04](REQUIREMENTS.md#nfr-04-performance-of-the-slot-list) | SC-15 | web + SQLite on one Starter instance | [ADR-002](adr/ADR-002-sqlite-on-persistent-disk.md), [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | [T4](architecture/TRADEOFF_MATRIX.md) | `tests/perf/locustfile.py` (20 users, 60 s, p95) | R8 |
| [NFR-05](REQUIREMENTS.md#nfr-05-testability-of-booking-rules) | SC-04, SC-05, SC-11, SC-12 | domain (pure, `I = 0`) | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | [T2](architecture/TRADEOFF_MATRIX.md) | mutmut report + coverage report on `app/domain` | R3 |
| [NFR-06](REQUIREMENTS.md#nfr-06-recoverability) | — (operational drill) | Render disk + daily snapshots | [ADR-002](adr/ADR-002-sqlite-on-persistent-disk.md) | [T6](architecture/TRADEOFF_MATRIX.md) | Timed restore drill recorded in the runbook | R5 |
| [NFR-07](REQUIREMENTS.md#nfr-07-time-correctness) | SC-15 | domain (injected `now`) + template filter | [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | [T2](architecture/TRADEOFF_MATRIX.md) | `tests/test_no_clock_in_domain.py` + SC-15 test | R6 |
| [NFR-08](REQUIREMENTS.md#nfr-08-usability-of-booking) | SC-04 | web: templates (mobile layout) | [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | [T1](architecture/TRADEOFF_MATRIX.md) | `tests/e2e/test_booking_clicks.py` (Playwright, 375 px) | — |

## Reverse checks

**ADRs → requirements** (every ADR's "Related requirements" appear above):

| ADR | Requirements |
|---|---|
| [ADR-001](adr/ADR-001-server-rendered-modular-monolith.md) | FR-06, FR-07, FR-13, FR-14, NFR-04, NFR-05, NFR-08 |
| [ADR-002](adr/ADR-002-sqlite-on-persistent-disk.md) | NFR-01, NFR-04, NFR-06, FR-09 |
| [ADR-003](adr/ADR-003-db-enforced-double-booking-prevention.md) | FR-09, FR-10, FR-11, NFR-01 |
| [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md) | FR-04, FR-08, FR-12, NFR-05, NFR-07 |

**Scenarios → requirements:** every scenario SC-01 to SC-16 appears in at least one row above. This is checked automatically.

**Non-goals:** NG-01 to NG-10 in the [charter](CHARTER.md#4-explicit-non-goals) intentionally have no requirements.

## Verification record

| Date | Command | Result | By |
|---|---|---|---|
| 2026-10-21 | `python tools/check_m1.py` | see output in README | (member name) |
