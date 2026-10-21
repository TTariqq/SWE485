# RULES.md: Team rules and project memory

This file is the team-owned project memory. DEVAI is given this file at the start of every session. Both members must agree to changes, made through a reviewed PR.

## Project facts
- Product: Office Hours Booking, a web app. Roles: `student`, `instructor`.
- **Language: Python 3.12** (declared at M1; it must not change).
- Stack (Option A, [ADR-001](docs/adr/ADR-001-server-rendered-modular-monolith.md)): FastAPI, Jinja2, SQLAlchemy 2.x, SQLite, pytest, mutmut, coverage.py, ruff, bandit, gitleaks, pip-audit.
- Deployment: one Render web service with a persistent disk.
- Data: **synthetic only**. Emails use `@example.edu`. Never use real student or staff data.

## Architecture rules (checked in the coupling check)
1. Dependencies only go downward: `web → services → domain`, and `services → repositories → models`.
2. `app/domain` imports **only** the standard library. No `fastapi`, `sqlalchemy` or `app.*` outside `app.domain`.
3. `app/domain` never calls `datetime.now()`. Pass `now: datetime` (UTC, timezone-aware) in as a parameter.
4. Only `app/repositories` runs database queries. Templates contain no rule logic.
5. No circular imports. `cancel_block` lives in the services layer and calls the repositories. It does not import other services.
6. All timestamps are stored in UTC and converted to Asia/Riyadh only in templates and form parsing.
7. Rule constants live in `app/domain/constants.py` and match [REQUIREMENTS.md](docs/REQUIREMENTS.md).

## Before prompting DEVAI (SPEC first)
Write or update `specs/SPEC-<feature>.md` **before** generating code. It must contain:
- the goal, and the requirement IDs it covers
- Given–When–Then criteria with **one failure path and one boundary case**
- constraints, non-goals, input/output and error contracts, and a worked example
- the source files to give as context, and the security constraints
- tests with an independent oracle (expected values worked out by hand, not by the code)

## Git workflow
- Short-lived branches: `feat/<id>-<short-name>`, `fix/...`, `docs/...`.
- **Commit raw AI output separately** from human fixes:
  - `raw(ai): <what> [DEVAI <model>]`, containing the unedited generated code
  - `fix(human): <what changed and why>`
- Add `Co-authored-by:` trailers for AI-generated commits as required by the course.
- Never rebase or squash away a raw/fix pair, yours or your partner's.
- Merge conflicts: resolve in a new human commit that explains the reconciliation.
- Every PR is reviewed by the other member. The reviewer is named in [AI_USE_DISCLOSURE.md](AI_USE_DISCLOSURE.md).

## Architecture decisions
- New decisions get a new ADR in `docs/adr/`.
- **Never rewrite an accepted ADR.** To change one, write a new ADR with `Supersedes: ADR-00X`, and set the old one's status to `Superseded by ADR-00Y`.

## Security rules
- No secrets in git. `.env` is ignored. `.env.example` holds fake values only.
- gitleaks runs as a pre-commit hook and in CI.
- Never paste secrets, personal data or proprietary material into DEVAI.
- Exclude `.env`, `*.db` and `backups/` from AI tool context.
- Verify every new dependency exists on PyPI and is the intended package before adding it.

## Checks run independently of the assistant
`ruff check .` · `pytest --cov=app --cov-branch` · `mutmut run --paths-to-mutate app/domain` · `bandit -r app` · `gitleaks detect` · `pip-audit` · `python tools/check_m1.py`
