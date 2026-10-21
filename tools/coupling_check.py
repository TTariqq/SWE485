"""Manual coupling check for the M1 architecture options.

Each option's module/container dependency graph is written below. It mirrors
the diagrams in docs/architecture/ARCHITECTURE_OPTIONS.md. The script checks
four rules and computes instability per module, then writes the result into
docs/architecture/COUPLING_CHECK.md between the GENERATED markers.

This is a supplement to the course's coupling detector, not a replacement:
attach the official detector report as well.

Rules:
  R-C1  No dependency cycles.
  R-C2  The domain module has no outgoing dependencies (pure).
  R-C3  At most one deployable unit writes to each datastore (no shared schema).
  R-C4  Only the persistence layer touches the datastore.

Run:  python tools/coupling_check.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "architecture" / "COUPLING_CHECK.md"

# graph: module -> set of modules it depends on
# kinds: which node is the domain, which are datastores, which are persistence
# layer modules, and which deployable unit each module belongs to
OPTIONS = {
    "Draft 0 (AI first draft)": {
        "graph": {
            "routes/bookings": {"routes/blocks", "templates/slots", "DB"},
            "routes/blocks": {"routes/bookings", "DB"},
            "templates/slots": set(),
            "cleanup": {"DB"},
            "DB": set(),
        },
        "domain": None,  # no separate domain module exists, so rules are in routes
        "datastores": {"DB"},
        "persistence": set(),
        "unit": {"routes/bookings": "web", "routes/blocks": "web",
                 "templates/slots": "web", "cleanup": "cleanup-script", "DB": "db"},
    },
    "Option A (chosen)": {
        "graph": {
            "web": {"services"},
            "services": {"domain", "repositories"},
            "domain": set(),
            "repositories": {"models", "DB"},
            "models": set(),
            "cli": {"services"},
            "DB": set(),
        },
        "domain": "domain",
        "datastores": {"DB"},
        "persistence": {"repositories"},
        "unit": {"web": "web", "services": "web", "domain": "web", "repositories": "web",
                 "models": "web", "cli": "web", "DB": "db"},
    },
    "Option B": {
        "graph": {
            "spa": {"api-routes"},  # over HTTP/JSON
            "api-routes": {"services"},
            "services": {"domain", "repositories"},
            "domain": set(),
            "repositories": {"models", "PG"},
            "models": set(),
            "PG": set(),
        },
        "domain": "domain",
        "datastores": {"PG"},
        "persistence": {"repositories"},
        "unit": {"spa": "static-site", "api-routes": "api", "services": "api", "domain": "api",
                 "repositories": "api", "models": "api", "PG": "postgres"},
    },
}


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Return strongly connected components with more than one node (Tarjan)."""
    index, low, stack, on, out = {}, {}, [], set(), []
    counter = [0]

    def strong(v: str) -> None:
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in graph.get(v, ()):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp))

    for v in graph:
        if v not in index:
            strong(v)
    return out


def instability(graph: dict[str, set[str]]) -> dict[str, tuple[int, int, float]]:
    """Ce = outgoing deps, Ca = incoming deps, I = Ce / (Ca + Ce)."""
    ca = {v: 0 for v in graph}
    for v, deps in graph.items():
        for w in deps:
            ca[w] = ca.get(w, 0) + 1
    res = {}
    for v in graph:
        ce = len(graph[v])
        total = ca[v] + ce
        res[v] = (ca[v], ce, ce / total if total else 0.0)
    return res


def check(opt: dict) -> list[tuple[str, bool, str]]:
    g = opt["graph"]
    results = []
    cycles = find_cycles(g)
    results.append(("R-C1 no cycles", not cycles,
                    "none" if not cycles else "; ".join(" <-> ".join(c) for c in cycles)))
    if opt["domain"] is None:
        results.append(("R-C2 pure domain", False, "no domain module: rules live in routes/templates"))
    else:
        deps = g[opt["domain"]]
        results.append(("R-C2 pure domain", not deps, "0 outgoing deps" if not deps else ", ".join(sorted(deps))))
    bad = []
    for ds in opt["datastores"]:
        writers = {opt["unit"][v] for v, d in g.items() if ds in d}
        if len(writers) > 1:
            bad.append(f"{ds} written by units {sorted(writers)}")
    results.append(("R-C3 one writer unit per datastore", not bad, "ok" if not bad else "; ".join(bad)))
    touching = sorted(v for v, d in g.items() if d & opt["datastores"] and v not in opt["persistence"])
    results.append(("R-C4 only persistence touches datastore", not touching,
                    "ok" if not touching else "touched by: " + ", ".join(touching)))
    return results


def build_report() -> str:
    out = ["_Generated by `python tools/coupling_check.py`._\n"]
    for name, opt in OPTIONS.items():
        res = check(opt)
        verdict = "CLEARED" if all(ok for _, ok, _ in res) else "FLAGGED"
        out.append(f"### {name}: **{verdict}**\n")
        out.append("| Rule | Result | Detail |")
        out.append("|---|---|---|")
        for rule, ok, detail in res:
            out.append(f"| {rule} | {'PASS' if ok else 'FAIL'} | {detail} |")
        out.append("")
        out.append("| Module | Ca (in) | Ce (out) | Instability I = Ce/(Ca+Ce) |")
        out.append("|---|---|---|---|")
        for m, (ca, ce, i) in instability(opt["graph"]).items():
            out.append(f"| {m} | {ca} | {ce} | {i:.2f} |")
        units = sorted(set(opt["unit"].values()))
        out.append(f"\nDeployable units/datastores: {len(units)} ({', '.join(units)})\n")
    return "\n".join(out)


def main() -> None:
    report = build_report()
    text = DOC.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- BEGIN GENERATED -->\n).*?(<!-- END GENERATED -->)",
                 lambda m: m.group(1) + report + "\n" + m.group(2), text, flags=re.S)
    DOC.write_text(new, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
