"""M1 consistency checker.

Checks:
  1. Every relative Markdown link points to an existing file and heading anchor.
  2. Every FR/NFR in REQUIREMENTS.md appears in TRACEABILITY.md (no orphans).
  3. Every scenario, user story and use case appears in TRACEABILITY.md or is
     referenced by a requirement.
  4. ADR lint: required fields present, rejected alternative and accepted
     downside sections non-empty, related requirement IDs exist.
  5. Risk register: every risk has an owner and a numeric threshold.
  6. Scope caps: endpoints <= 10, screens <= 6, tables <= 8.

Exit code 0 if all checks pass, 1 otherwise.
Run:  python tools/check_m1.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REQ = DOCS / "REQUIREMENTS.md"
TRACE = DOCS / "TRACEABILITY.md"
RISKS = DOCS / "RISK_REGISTER.md"

errors: list[str] = []
passes: list[str] = []


def slug(heading: str) -> str:
    """GitHub-style heading anchor."""
    h = heading.strip().lower()
    h = re.sub(r"[`*_~]", "", h)
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    out, seen = set(), {}
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        m = re.match(r"^#{1,6}\s+(.*)$", line)
        if m and not in_code:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            out.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
    return out


def check_links() -> None:
    count = 0
    for md in ROOT.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if re.match(r"^(https?:|mailto:)", target):
                continue
            count += 1
            path_part, _, anchor = target.partition("#")
            dest = (md.parent / path_part).resolve() if path_part else md
            if not dest.exists():
                errors.append(f"Broken link in {md.relative_to(ROOT)}: {target} (file not found)")
                continue
            if anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                errors.append(f"Broken anchor in {md.relative_to(ROOT)}: {target}")
    passes.append(f"Checked {count} relative links")


def check_traceability() -> None:
    req = REQ.read_text(encoding="utf-8")
    trace = TRACE.read_text(encoding="utf-8")
    reqs = re.findall(r"^#### ((?:FR|NFR)-\d+)", req, flags=re.M)
    orphans = [r for r in reqs if f"[{r}](" not in trace]
    for r in orphans:
        errors.append(f"Orphan requirement (not in traceability matrix): {r}")
    passes.append(f"{len(reqs)} requirements, {len(orphans)} orphans")

    for prefix in ("SC", "US", "UC"):
        ids = sorted(set(re.findall(rf"\b({prefix}-\d+)\b", req)))
        missing = [i for i in ids if not re.search(rf"\b{i}\b", trace)]
        for i in missing:
            errors.append(f"{i} defined in REQUIREMENTS.md but not traced in TRACEABILITY.md")
        passes.append(f"{len(ids)} {prefix} IDs, {len(missing)} untraced")

    # every FR has at least one scenario
    for block in re.split(r"^#### ", req, flags=re.M)[1:]:
        rid = block.split()[0]
        if rid.startswith("FR-") and not re.search(r"SC-\d+", block):
            errors.append(f"{rid} has no scenario")


def check_adrs() -> None:
    req_ids = set(re.findall(r"^#### ((?:FR|NFR)-\d+)", REQ.read_text(encoding="utf-8"), flags=re.M))
    adrs = sorted((DOCS / "adr").glob("ADR-*.md"))
    if len(adrs) < 3:
        errors.append(f"Only {len(adrs)} ADRs (need >= 3)")
    for adr in adrs:
        t = adr.read_text(encoding="utf-8")
        name = adr.name
        for field in ("**Status:**", "**Date:**", "**Related requirements:**", "**Supersedes:**"):
            if field not in t:
                errors.append(f"{name}: missing field {field}")
        for section in ("## Context", "## Decision", "## Rejected alternative", "## Accepted downside"):
            m = re.search(rf"^{re.escape(section)}\n(.*?)(?=^## |\Z)", t, flags=re.M | re.S)
            if not m or len(m.group(1).strip()) < 40:
                errors.append(f"{name}: section '{section}' missing or too short")
        rel = re.search(r"\*\*Related requirements:\*\*(.*)", t)
        if rel:
            ids = re.findall(r"(?:FR|NFR)-\d+", rel.group(1))
            if not ids:
                errors.append(f"{name}: no requirement IDs listed")
            for i in ids:
                if i not in req_ids:
                    errors.append(f"{name}: unknown requirement {i}")
        status = re.search(r"\*\*Status:\*\*\s*(\w+)", t)
        if status and status.group(1) not in ("Proposed", "Accepted", "Superseded", "Deprecated"):
            errors.append(f"{name}: invalid status {status.group(1)}")
    passes.append(f"{len(adrs)} ADRs linted")


def check_risks() -> None:
    rows = [line for line in RISKS.read_text(encoding="utf-8").splitlines()
            if re.match(r"^\|\s*\**R\d+", line)]
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        rid = cells[0].strip("*")
        threshold, owner = cells[5], cells[7]
        if not re.search(r"\d", threshold):
            errors.append(f"{rid}: alert threshold has no measurable number")
        if not owner or owner == "-":
            errors.append(f"{rid}: no owner")
    passes.append(f"{len(rows)} risks checked for owner and numeric threshold")


def check_scope() -> None:
    req = REQ.read_text(encoding="utf-8")
    endpoints = re.findall(r"^\| E\d+ \|", req, flags=re.M)
    screens = re.findall(r"\bS\d+ [A-Z]", req.split("**Screens")[1].split("\n")[0]) if "**Screens" in req else []
    tables_line = re.search(r"\*\*Tables \(.*?\):\*\*(.*)", req)
    tables = re.findall(r"`(\w+)`", tables_line.group(1)) if tables_line else []
    for label, n, cap in (("endpoints", len(endpoints), 10), ("screens", len(screens), 6), ("tables", len(tables), 8)):
        if n > cap:
            errors.append(f"Scope cap exceeded: {n} {label} > {cap}")
        passes.append(f"{label}: {n}/{cap}")


def main() -> int:
    check_links()
    check_traceability()
    check_adrs()
    check_risks()
    check_scope()
    for p in passes:
        print(f"PASS  {p}")
    for e in errors:
        print(f"FAIL  {e}")
    print(f"\n{'ALL CHECKS PASSED' if not errors else f'{len(errors)} PROBLEM(S) FOUND'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
