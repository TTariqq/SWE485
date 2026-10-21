# ADR-004: Store times in UTC and pass the current time into domain rules

- **Status:** Accepted
- **Date:** 2026-10-21
- **Deciders:** Tariq Algadheeb, Abdullah
- **Supersedes:** none
- **Related requirements:** FR-04, FR-08, FR-12, NFR-05, NFR-07
- **Trade-off matrix rows:** T2

## Context
Most of our rules are about time: the booking window (FR-08), the cancel cutoff (FR-12) and slot generation (FR-04). Our boundary scenarios are 1 minute apart (SC-04/05 and SC-11/12). If the rules read the system clock, the tests can't control "now", and the boundary tests become flaky or hollow. Render servers run in UTC, while users are in Riyadh (UTC+03:00).

## Decision
- Store every timestamp as **UTC, timezone-aware**. Convert to Asia/Riyadh only when parsing form input and rendering templates.
- Every domain function that depends on time takes **`now: datetime` as a parameter**, e.g. `check_booking(slot, student_bookings, now)`. Only the service layer calls `datetime.now(timezone.utc)`.
- A test enforces that `app/domain` contains no call to `datetime.now(` (NFR-07 measure).

## Rejected alternative
**Store naive local (Riyadh) times and call `datetime.now()` inside the rules.** It is simpler to write at first, but it was rejected because:
- boundary tests can't fix "now";
- naive datetimes compare wrongly with timezone-aware ones;
- it would break if the server's timezone setting ever changed.

## Accepted downside
- **More conversion code** at the edges: form parsing and template filters. Forgetting a conversion shows times 3 hours off, so SC-15 must have a test.
- **Every domain function signature carries `now`,** which makes calls slightly longer.

## Consequences
- The boundary tests (SC-04, SC-05, SC-06, SC-11, SC-12) use fixed `now` values, so they are deterministic and good targets for mutation testing.
