"""Cost model for Office Hours Booking (M1).

Computes monthly hosting cost for Option A and Option B, and the development
AI (DEVAI) cost, from stated assumptions and published rates. Then runs a
sensitivity analysis. Writes the results into docs/COST_MODEL.md between the
GENERATED markers, so the arithmetic in the document is always reproducible.

Run:  python tools/cost_model.py
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "COST_MODEL.md"
TOKEN_LOG = ROOT / "tools" / "token_log.csv"

# ---------------------------------------------------------------------------
# 1. Published rates (USD). Re-verify on https://render.com/pricing before
#    submitting and update RATES_CHECKED_ON. Sources are listed in COST_MODEL.md.
# ---------------------------------------------------------------------------
RATES_CHECKED_ON = "2026-10-21"
RATES = {
    "workspace_hobby_per_month": 0.00,      # Hobby workspace
    "web_starter_per_month": 7.00,          # Starter instance, 512 MB, 0.5 CPU
    "disk_per_gb_month": 0.25,              # persistent SSD disk
    "static_site_per_month": 0.00,          # static sites have no instance fee
    "pg_basic_256mb_per_month": 6.00,       # Render Postgres Basic-256mb
    "pg_storage_per_gb_month": 0.30,        # Postgres storage
    "bandwidth_included_gb": 5.0,           # Hobby, after 1 Aug 2026 (conservative)
    "bandwidth_overage_per_gb": 0.15,
    # DEVAI model rates: EXAMPLE VALUES. Replace with the published rate of the
    # model DEVAI uses (or the course's stated equivalent rate).
    "ai_input_per_mtok": 3.00,
    "ai_output_per_mtok": 15.00,
}
AI_RATES_ARE_EXAMPLE = True

# ---------------------------------------------------------------------------
# 2. Usage assumptions (pilot: one department, one semester)
# ---------------------------------------------------------------------------
USAGE = {
    "students": 400,                 # S
    "instructors": 20,               # I
    "student_sessions_per_week": 1.5,  # b: visits per student per week
    "instructor_sessions_per_week": 5,
    "weeks_per_month": 4.33,
    "pages_per_session": 6,          # v: login, slots, book, my bookings, ...
    # Option A: server-rendered HTML page incl. CSS (KB)
    "a_page_kb": 30,
    # Option B: SPA bundle (KB), browser-cache hit rate, API calls per page, JSON KB
    "b_bundle_kb": 250,
    "b_cache_hit_rate": 0.70,
    "b_api_calls_per_page": 2,
    "b_json_kb": 5,
    "disk_gb": 1,                    # smallest practical size
    "pg_storage_gb": 1,
}

# Development (DEVAI) assumptions, used only if token_log.csv has no measured rows
DEV = {
    "members": 2,
    "weeks": 6,                      # 21 Oct to 3 Dec 2026
    "sessions_per_member_per_week": 10,
    "turns_per_session": 8,
    "output_tokens_per_turn": 800,
    # context re-sent each turn: measured from these files (chars / 4 heuristic)
    "context_files": ["RULES.md", "docs/REQUIREMENTS.md"],
    "extra_code_context_tokens": 3000,  # ~2 source files attached per prompt
}


def approx_tokens(text: str) -> int:
    """Approximate token count: about 4 characters per token for English text/code."""
    return math.ceil(len(text) / 4)


def measured_context_tokens() -> int:
    total = 0
    for rel in DEV["context_files"]:
        p = ROOT / rel
        if p.exists():
            total += approx_tokens(p.read_text(encoding="utf-8"))
    return total + DEV["extra_code_context_tokens"]


def sessions_per_month(u: dict) -> float:
    return (u["students"] * u["student_sessions_per_week"]
            + u["instructors"] * u["instructor_sessions_per_week"]) * u["weeks_per_month"]


def bandwidth_gb(option: str, u: dict) -> float:
    n = sessions_per_month(u)
    if option == "A":
        kb = n * u["pages_per_session"] * u["a_page_kb"]
    else:
        per_session = (u["b_bundle_kb"] * (1 - u["b_cache_hit_rate"])
                       + u["pages_per_session"] * u["b_api_calls_per_page"] * u["b_json_kb"])
        kb = n * per_session
    return kb / 1024 / 1024


def bandwidth_cost(gb: float, r: dict) -> float:
    return max(0.0, gb - r["bandwidth_included_gb"]) * r["bandwidth_overage_per_gb"]


def hosting_cost(option: str, u: dict, r: dict) -> dict:
    gb = bandwidth_gb(option, u)
    if option == "A":
        fixed = (r["workspace_hobby_per_month"] + r["web_starter_per_month"]
                 + u["disk_gb"] * r["disk_per_gb_month"])
    else:
        fixed = (r["workspace_hobby_per_month"] + r["static_site_per_month"]
                 + r["web_starter_per_month"] + r["pg_basic_256mb_per_month"]
                 + u["pg_storage_gb"] * r["pg_storage_per_gb_month"])
    bw = bandwidth_cost(gb, r)
    return {"fixed": fixed, "bandwidth_gb": gb, "bandwidth_cost": bw, "total": fixed + bw}


def read_token_log() -> list[dict]:
    if not TOKEN_LOG.exists():
        return []
    with TOKEN_LOG.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("input_tokens", "").strip()]
    return rows


def dev_ai_cost(r: dict, token_factor: float = 1.0) -> dict:
    rows = read_token_log()
    if rows:
        tin = sum(int(x["input_tokens"]) for x in rows)
        tout = sum(int(x["output_tokens"]) for x in rows)
        basis = f"MEASURED: {len(rows)} logged DEVAI sessions in tools/token_log.csv"
    else:
        ctx = measured_context_tokens()
        sessions = DEV["members"] * DEV["weeks"] * DEV["sessions_per_member_per_week"]
        tin = sessions * DEV["turns_per_session"] * ctx
        tout = sessions * DEV["turns_per_session"] * DEV["output_tokens_per_turn"]
        basis = (f"ESTIMATED: no measured rows yet. {sessions} sessions x "
                 f"{DEV['turns_per_session']} turns x {ctx:,} context tokens (measured from files)")
    tin *= token_factor
    tout *= token_factor
    cost = tin / 1e6 * r["ai_input_per_mtok"] + tout / 1e6 * r["ai_output_per_mtok"]
    return {"input_tokens": tin, "output_tokens": tout, "cost": cost, "basis": basis}


def money(x: float) -> str:
    return f"${x:,.2f}"


def build_report() -> str:
    r, u = RATES, USAGE
    out = []
    a, b = hosting_cost("A", u, r), hosting_cost("B", u, r)
    n = sessions_per_month(u)

    out.append(f"_Generated by `python tools/cost_model.py`. Rates checked on {RATES_CHECKED_ON}._\n")
    out.append("### Baseline monthly hosting\n")
    out.append(f"Sessions per month = (S x b + I x 5) x 4.33 = "
               f"({u['students']} x {u['student_sessions_per_week']} + {u['instructors']} x "
               f"{u['instructor_sessions_per_week']}) x {u['weeks_per_month']} = **{n:,.0f}**\n")
    out.append("| Item | Option A | Option B |")
    out.append("|---|---|---|")
    out.append(f"| Workspace (Hobby) | {money(r['workspace_hobby_per_month'])} | {money(r['workspace_hobby_per_month'])} |")
    out.append(f"| Web service (Starter) | {money(r['web_starter_per_month'])} | {money(r['web_starter_per_month'])} |")
    out.append(f"| Disk {u['disk_gb']} GB x {money(r['disk_per_gb_month'])} | {money(u['disk_gb'] * r['disk_per_gb_month'])} | n/a |")
    out.append(f"| Static site | n/a | {money(r['static_site_per_month'])} |")
    out.append(f"| Postgres Basic-256mb | n/a | {money(r['pg_basic_256mb_per_month'])} |")
    out.append(f"| Postgres storage {u['pg_storage_gb']} GB x {money(r['pg_storage_per_gb_month'])} | n/a | {money(u['pg_storage_gb'] * r['pg_storage_per_gb_month'])} |")
    out.append(f"| Bandwidth used (GB) | {a['bandwidth_gb']:.2f} | {b['bandwidth_gb']:.2f} |")
    out.append(f"| Bandwidth overage (> {r['bandwidth_included_gb']:.0f} GB) | {money(a['bandwidth_cost'])} | {money(b['bandwidth_cost'])} |")
    out.append(f"| **Total per month** | **{money(a['total'])}** | **{money(b['total'])}** |")
    out.append(f"| **Pilot semester (4 months)** | **{money(4 * a['total'])}** | **{money(4 * b['total'])}** |\n")

    out.append("### Sensitivity: number of users (all usage scaled together)\n")
    out.append("| Scale | Students | Sessions/month | A bandwidth GB | A total/month | B bandwidth GB | B total/month |")
    out.append("|---|---|---|---|---|---|---|")
    for f in (0.5, 1, 10, 50, 100):
        uu = dict(u, students=u["students"] * f, instructors=u["instructors"] * f)
        ha, hb = hosting_cost("A", uu, r), hosting_cost("B", uu, r)
        out.append(f"| x{f:g} | {uu['students']:,.0f} | {sessions_per_month(uu):,.0f} | "
                   f"{ha['bandwidth_gb']:.2f} | {money(ha['total'])} | {hb['bandwidth_gb']:.2f} | {money(hb['total'])} |")
    # break-even point where A's bandwidth overage makes it as expensive as B
    out.append("")
    per_gb_a = u["pages_per_session"] * u["a_page_kb"] / 1024 / 1024
    per_gb_b = (u["b_bundle_kb"] * (1 - u["b_cache_hit_rate"])
                + u["pages_per_session"] * u["b_api_calls_per_page"] * u["b_json_kb"]) / 1024 / 1024
    if per_gb_a > per_gb_b:
        # A's cost minus B's cost as a function of sessions/month; find where it reaches 0
        def diff(sessions: float) -> float:
            over_a = max(0.0, sessions * per_gb_a - r["bandwidth_included_gb"])
            over_b = max(0.0, sessions * per_gb_b - r["bandwidth_included_gb"])
            return (a["fixed"] + over_a * r["bandwidth_overage_per_gb"]) - (b["fixed"] + over_b * r["bandwidth_overage_per_gb"])
        lo, hi = 0.0, 1e9
        for _ in range(200):  # bisection
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if diff(mid) < 0 else (lo, mid)
        sessions_be = hi
        out.append(f"Break-even (approximate): Option A only becomes more expensive than B above about "
                   f"**{sessions_be:,.0f} sessions/month** (about {sessions_be / n:,.0f}x the pilot), because "
                   f"A sends {per_gb_a * 1024 * 1024:.0f} KB per session vs {per_gb_b * 1024 * 1024:.0f} KB for B.\n")

    out.append("### Sensitivity: bandwidth allowance (rate uncertainty)\n")
    out.append("| Included bandwidth | A at x100 scale | B at x100 scale |")
    out.append("|---|---|---|")
    u100 = dict(u, students=u["students"] * 100, instructors=u["instructors"] * 100)
    for inc in (5.0, 100.0):
        rr = dict(r, bandwidth_included_gb=inc)
        out.append(f"| {inc:.0f} GB | {money(hosting_cost('A', u100, rr)['total'])} | {money(hosting_cost('B', u100, rr)['total'])} |")
    out.append("")

    out.append("### Development AI cost (DEVAI)\n")
    d = dev_ai_cost(r)
    flag = " **(EXAMPLE rates, replace with DEVAI's published rate)**" if AI_RATES_ARE_EXAMPLE else ""
    out.append(f"- Basis: {d['basis']}")
    out.append(f"- Rates: {money(r['ai_input_per_mtok'])} / M input tokens, "
               f"{money(r['ai_output_per_mtok'])} / M output tokens{flag}")
    out.append(f"- Input tokens: {d['input_tokens']:,.0f}; output tokens: {d['output_tokens']:,.0f}")
    out.append(f"- Cost = {d['input_tokens']:,.0f} / 1,000,000 x {r['ai_input_per_mtok']} + "
               f"{d['output_tokens']:,.0f} / 1,000,000 x {r['ai_output_per_mtok']} = **{money(d['cost'])}** for the project\n")
    out.append("| Token volume | Project AI cost |")
    out.append("|---|---|")
    for f in (0.5, 1, 2):
        out.append(f"| x{f:g} | {money(dev_ai_cost(r, f)['cost'])} |")
    out.append("")
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
