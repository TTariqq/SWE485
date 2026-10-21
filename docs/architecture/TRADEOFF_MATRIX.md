# Trade-off Matrix: Option A vs Option B

**Scale:** each option scores 1 (poor) to 5 (excellent) on each row. Weighted score = weight × score. The weights add up to 100, so the maximum total is 500.

| Row | Criterion (linked requirements) | Weight | A score | A weighted | B score | B weighted | Why |
|---|---|---|---|---|---|---|---|
| **T1** | Implementation effort for 2 students by M2 (charter success criteria) | 20 | 5 | 100 | 2 | 40 | A: one language, one deployable unit. B: adds React/TypeScript, a build step, CORS and JWT. |
| **T2** | Testability of rules (NFR-05, NFR-07) | 15 | 5 | 75 | 4 | 60 | Both have a pure domain. B's end-to-end tests need both the SPA and the API running. |
| **T3** | Booking integrity under concurrency (NFR-01, FR-09) | 15 | 4 | 60 | 5 | 75 | A: single writer + partial index (ADR-003), but tied to SQLite. B: Postgres row locks are more robust with many writers. |
| **T4** | Slot-list performance at pilot load (NFR-04) | 10 | 4 | 40 | 4 | 40 | A: local file, no network hop, full HTML per page. B: fast JSON, but a 250 KB first load and a network hop to the DB. |
| **T5** | Security surface (NFR-02, NFR-03) | 10 | 4 | 40 | 3 | 30 | A: HttpOnly session cookie, needs CSRF tokens. B: storing the JWT in the browser, CORS rules, token expiry. |
| **T6** | Operability and recovery (NFR-06) | 10 | 3 | 30 | 4 | 40 | A: daily disk snapshot (≤ 24 h data loss), downtime on deploy. B: managed database backups, rolling deploys. |
| **T7** | Monthly cost at pilot ([COST_MODEL.md](../COST_MODEL.md)) | 5 | 5 | 25 | 3 | 15 | A ≈ $7.25 vs B ≈ $13.30 per month. |
| **T8** | Extensibility: mobile app, more instances (NG-07) | 5 | 2 | 10 | 5 | 25 | B already has a JSON API and can scale out. A is single-instance (ADR-002). |
| **T9** | Coupling and number of deployable units ([COUPLING_CHECK.md](COUPLING_CHECK.md)) | 10 | 5 | 50 | 3 | 30 | A: 1 unit, a one-way layer graph. B: 3 units, and the SPA and API must agree on the API contract. |
| | **Total (out of 500)** | **100** | | **430 (86%)** | | **355 (71%)** | |

**Decision:** Option A ([ADR-001](../adr/ADR-001-server-rendered-modular-monolith.md)).

## Where B wins (what we gave up)
Rows **T3**, **T6** and **T8**: concurrency robustness, recovery and extensibility. These are accepted downsides in [ADR-002](../adr/ADR-002-sqlite-on-persistent-disk.md) and [ADR-003](../adr/ADR-003-db-enforced-double-booking-prevention.md), and they are tracked as risks R1 and R5 in the [risk register](../RISK_REGISTER.md).

## Weight sensitivity
Does the decision change if we had judged the weights differently?

| Change | A total | B total | Winner |
|---|---|---|---|
| Baseline | 430 | 355 | A |
| Halve T1 (effort 20 → 10) and triple T8 (extensibility 5 → 15) | 400 | 385 | A (narrowly) |
| T3 doubled (concurrency 15 → 30), T1 reduced (20 → 5) | 415 | 400 | A (narrowly) |
| Effort ignored (T1 = 0), extensibility 25 | 370 | 415 | **B** |

**Interpretation:** A wins unless we stop caring about delivery effort *and* treat a future mobile app or scaling as very important. Both of those contradict our charter (6-week course, NG-07).

## Using this matrix in the M1 review
When the instructor gives a quality-attribute scenario:
1. Find the NFR it matches (for example, "100 students book at 9:00" → NFR-01 / NFR-04).
2. Name the row (T3 / T4) and read out both scores.
3. State the decision and the ADR (ADR-003), the **rejected option**, and the **accepted downside** (single writer, tied to SQLite).
4. Point to the risk with its alert threshold (R1).
