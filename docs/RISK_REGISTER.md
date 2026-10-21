# Risk Register

**Scales:** Likelihood (L) and Impact (I) are each 1–3. Score = L × I. **Top three risks are bold.**

Every risk has a **measurable alert threshold**: a number or event that tells the owner to act. "Owner" is the named member who checks the threshold and leads the response.

| ID | Risk | L | I | Score | Alert threshold (measurable) | How it is checked | Owner | Mitigation / response |
|---|---|---|---|---|---|---|---|---|
| **R1** | **Double booking or bypassed per-student limits under concurrent requests** (NFR-01, ADR-003) | 2 | 3 | **6** | **≥ 1 row** returned by the integrity query (slot with > 1 active booking), **or ≥ 1 failure** in 100 runs of the 10-thread race test | Race test in CI on every PR; integrity query in a daily job | Tariq Algadheeb | Partial unique index + `BEGIN IMMEDIATE`; schema test asserts the index exists; if triggered: block the merge, fix, add a regression test |
| **R2** | **Vertical slice not working end to end by M2** (charter success criteria) | 2 | 3 | **6** | The end-to-end test `login → book → my bookings` is **not passing on main by Sun 26 Oct 2026, 23:59** | CI status on `main` | Abdullah | Build the booking path first (FR-01, FR-06, FR-07, FR-13) and cut other screens; daily 10-minute check-in |
| **R3** | **Hollow tests: suite passes despite faulty rules** (NFR-05) | 2 | 3 | **6** | **Mutation score < 80%** or **branch coverage < 90%** on `app/domain` | `mutmut` + `coverage` run before each milestone and in CI | Tariq Algadheeb | Independent oracle values in SPECs; test every boundary pair (SC-04/05, SC-11/12); kill surviving mutants before M2 |
| R4 | Live secret committed to git (pass condition) | 1 | 3 | 3 | **≥ 1 finding** from gitleaks on the full history | gitleaks pre-commit hook + CI | Abdullah | `.gitignore` for `.env`; `.env.example` with fakes; if triggered: rotate the secret immediately, then clean history with instructor guidance |
| R5 | Data loss on the single SQLite disk (NFR-06, ADR-002) | 1 | 3 | 3 | Latest successful disk snapshot **older than 26 hours**, or restore drill takes **> 15 minutes** | Render dashboard snapshot list (checked weekly); restore drill before M4 | Abdullah | Daily automatic snapshots; runbook restore steps; timed drill |
| R6 | Time-zone bug shows slots at the wrong time (NFR-07, ADR-004) | 2 | 2 | 4 | **≥ 1 failing** time test (SC-15), **or ≥ 1** `datetime.now(` found in `app/domain` | pytest + grep test in CI | Tariq Algadheeb | UTC storage, injected `now`, one template filter for Riyadh time |
| R7 | AI-generated code merged that no member can explain (core standard) | 2 | 3 | 6 | **≥ 1 merged file** without a named reader in the disclosure log, or **≥ 1 PR** without a raw/fix commit pair | PR checklist; review of the disclosure log at each milestone | Both (each for own PRs) | Raw/fix commit rule in RULES.md; reviewer explains the change back in the PR |
| R8 | Hosting cost or plan change exceeds budget | 1 | 1 | 1 | Monthly bill **> $10**, or bandwidth **> 4 GB (80% of 5 GB)** in a month | Render billing page, monthly | Abdullah | Re-run the cost model; reduce page size; switch plan |
| R9 | Hallucinated or wrong dependency installed (M3 security) | 1 | 2 | 2 | **≥ 1 package** in `requirements.txt` not verified on PyPI (name, author, downloads), or **≥ 1** high-severity `pip-audit` finding | Manual check per new dependency; pip-audit in CI | Tariq Algadheeb | Pin versions; verify each new package before adding it |

**Note:** R7 also scores 6. R1–R3 are listed as the top three because they block milestone marks directly (M2 mutation and slice marks). R7 is controlled by a process rule that runs on every PR.

## Coherence notes
- Every NFR with a numeric measure has a matching threshold here: NFR-01 → R1, NFR-05 → R3, NFR-06 → R5, NFR-07 → R6.
- Rubric "coherence breaks addressed or explained": if the official coherence report flags a mismatch, add a row below.

| Date | Coherence issue reported | Resolution | Commit |
|---|---|---|---|
| | | | |
