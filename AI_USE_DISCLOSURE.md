# AI Use Disclosure Log

One page per milestone. Pairs rotate responsibility: **M1 log owner: [name]**.

---

## M1 Requirements and architecture (21 Oct 2026)

### 1. Tools and contribution

| Tool | Model | Mode | Purpose |
|---|---|---|---|
| Claude (Anthropic), Claude app | Claude Opus (claude-opus-5-5) | Chat with file generation | Generated the first draft of the full M1 package: charter, requirements, ADRs, architecture options and diagrams, trade-off matrix, risk register, cost-model and coupling-check scripts |
| DEVAI | [model] | [mode] | [fill in if used at M1, or write "not used at M1"] |

> ⚠️ **Approved-tool check:** the brief names **DEVAI** as the approved tool. Confirm with the instructor that using Claude to draft M1 documents is acceptable. If it isn't, regenerate or revise the package with DEVAI and update this table.

**AI contribution by area** (none / minor / substantial / primary):

| Area | AI contribution | Human contribution (fill in) |
|---|---|---|
| Charter, scope and non-goals | primary | |
| Personas, user stories, use cases, scenarios | primary | |
| Functional and non-functional requirements | primary | |
| Architecture options, C4 diagrams, Draft 0 | primary | |
| Trade-off matrix and weights | primary | |
| ADR-001 to ADR-004 | primary | |
| Cost model (script and rates lookup) | primary | |
| Coupling-check script | primary | |
| Risk register | primary | |
| Requirements correction log | none (human only) | |

**How Draft 0 was produced:** Draft 0 in [ARCHITECTURE_OPTIONS.md](docs/architecture/ARCHITECTURE_OPTIONS.md) was written by the AI as a deliberately naive "routes do everything" baseline, to show the coupling problems that Option A fixes. It was not a sincere first proposal. If the course requires the draft to be DEVAI's genuine first output, ask DEVAI for an architecture, save that output unchanged as Draft 0, and rerun the coupling detector on it.

### 2. Errors and rejections (fill in from your own review, at least one of each)

| Type | What the AI produced | How we detected it | What we did | Commit |
|---|---|---|---|---|
| AI error | | | | |
| Rejected suggestion | | | Reason: | |

*Places worth checking for errors: the rule constants, the trade-off scores and weights, the bandwidth allowance (two sources disagree), and the example DEVAI token rates.*

### 3. Provenance

- Raw AI output commit: `raw(ai): M1 package draft [Claude]`, hash: `________`
- Human fix commits: list hashes, or point to the [correction log](docs/REQUIREMENTS_CORRECTION_LOG.md)
- Co-authored-by trailer used on the raw commit: `Co-authored-by: Claude <noreply@anthropic.com>` (or the course's required format)

| Generated file | Member who read it in full |
|---|---|
| docs/CHARTER.md | |
| docs/REQUIREMENTS.md | |
| docs/TRACEABILITY.md | |
| docs/architecture/ARCHITECTURE_OPTIONS.md | |
| docs/architecture/TRADEOFF_MATRIX.md | |
| docs/architecture/COUPLING_CHECK.md | |
| docs/COST_MODEL.md + tools/cost_model.py | |
| tools/coupling_check.py, tools/check_m1.py | |
| docs/adr/ADR-001 … ADR-004 | |
| docs/RISK_REGISTER.md | |
| RULES.md | |

### 4. Data and licensing

- Data boundary: **synthetic only**. No real student or staff data, secrets or institutional documents were given to any AI tool.
- Dependencies: none installed at M1. The planned packages (FastAPI, SQLAlchemy, pytest, mutmut, …) will be verified on PyPI when added (risk R9).
- Retrieved sources cited in the cost model: [render.com/pricing](https://render.com/pricing), [render.com/docs/disks](https://render.com/docs/disks), [Render mid-2026 plan review](https://jwatte.com/blog/render-com-platform-review.md).
- Licensing: all documents are original to this project. The Mermaid diagram syntax is MIT-licensed tooling, and no third-party content is copied.

### 5. Individual ownership

> "I can explain and defend every part of this submission that carries my name."

| Member | Areas | Signature | Date |
|---|---|---|---|
| Tariq Algadheeb | | | |
| Abdullah | | | |

### 6. Cost

Not required at M1. The token logging method is in [COST_MODEL.md §3](docs/COST_MODEL.md#3-how-tokens-are-measured).
