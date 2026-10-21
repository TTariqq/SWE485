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
