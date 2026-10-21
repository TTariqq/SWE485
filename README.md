# Office Hours Booking (OHB)

Students book short office-hour slots with instructors; instructors publish their hours once. SWE485 project, **App** type, **Python 3.12**.

## M1 package (Requirements and architecture, due 21 Oct 2026)

| Rubric item | File |
|---|---|
| Charter: team, problem, scope, non-goals | [docs/CHARTER.md](docs/CHARTER.md) |
| Personas, user stories, use cases, scenarios, FR, NFR (quality-attribute scenarios) | [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) |
| Human correction log for the AI requirements draft | [docs/REQUIREMENTS_CORRECTION_LOG.md](docs/REQUIREMENTS_CORRECTION_LOG.md) |
| Traceability matrix (verified links) | [docs/TRACEABILITY.md](docs/TRACEABILITY.md) |
| Two options + AI draft, C4 Context and Container (Mermaid), distinctness check | [docs/architecture/ARCHITECTURE_OPTIONS.md](docs/architecture/ARCHITECTURE_OPTIONS.md) |
| Trade-off matrix | [docs/architecture/TRADEOFF_MATRIX.md](docs/architecture/TRADEOFF_MATRIX.md) |
| Coupling check + residual risk | [docs/architecture/COUPLING_CHECK.md](docs/architecture/COUPLING_CHECK.md) |
| Cost model (assumptions, rates, arithmetic, sensitivity) | [docs/COST_MODEL.md](docs/COST_MODEL.md) |
| ADRs (4) | [docs/adr/](docs/adr/) |
| Risk register (thresholds, owners) | [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md) |
| Declared language + team rules | [RULES.md](RULES.md) |
| AI-use disclosure | [AI_USE_DISCLOSURE.md](AI_USE_DISCLOSURE.md) |

## Reproducible checks (no AI needed)

```bash
python tools/check_m1.py       # links, orphans, ADR lint, risk thresholds, scope caps
python tools/cost_model.py     # regenerates numbers in docs/COST_MODEL.md
python tools/coupling_check.py # regenerates results in docs/architecture/COUPLING_CHECK.md
```

All three use only the Python standard library.

## Before you submit: things only the team can do

1. Add Abdullah's full name wherever "Abdullah" appears (charter, ADRs, risk register, disclosure).
2. Commit this package **unchanged first** as `raw(ai): M1 package draft [Claude]`, then make your edits in separate `fix(human): ...` commits.
3. Read every file. Fill in the [correction log](docs/REQUIREMENTS_CORRECTION_LOG.md) with at least 3–5 real changes you made.
4. Fill in the disclosure log: who read each file, one AI error, one rejected suggestion, and signatures.
5. Confirm with the instructor that drafting with a non-DEVAI tool is acceptable (see the disclosure log warning).
6. Re-verify the Render prices on render.com/pricing. Replace the **example** DEVAI token rates in `tools/cost_model.py` with the real ones, then rerun it.
7. Run the **official** course coupling detector, ADR linter and coherence check, and save their reports in the repo.
8. Run `python tools/check_m1.py` and record the result in the traceability verification table.
