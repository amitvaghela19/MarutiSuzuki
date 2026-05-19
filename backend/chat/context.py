"""Build rich analysis context for the supply-chain chatbot."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from backend.settings import settings

TIRE_SUPPLIER_IDS = frozenset(
    {"SUP-IN-TIRE", "SUP-AE-GULF-CHEM", "SUP-SA-CARBON", "SUP-MY-RUBBER", "SUP-TH-RUBBER"}
)
TIRE_KEYWORDS = re.compile(
    r"\b(mrf|tyre|tire|gulf|rubber|red\s*sea|carbon\s*black|feedstock)\b",
    re.I,
)


def load_latest_snapshot() -> dict[str, Any] | None:
    path = settings.snapshots_dir / "latest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _risk_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["id"]: r for r in snapshot.get("supplier_risks") or [] if r.get("id")}


def _supplier_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["id"]: s for s in snapshot.get("suppliers") or [] if s.get("id")}


def _fg_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fg = snapshot.get("fear_greed") or {}
    out = {fg["maruti_suzuki"]["id"]: fg["maruti_suzuki"]} if fg.get("maruti_suzuki") else {}
    for s in fg.get("suppliers") or []:
        if s.get("id"):
            out[s["id"]] = s
    return out


def _format_supplier_dossier(
    sid: str,
    suppliers: dict[str, dict],
    risks: dict[str, dict],
    fg: dict[str, dict],
) -> list[str]:
    s = suppliers.get(sid)
    if not s:
        return [f"  {sid}: (no supplier record)"]
    r = risks.get(sid, {})
    f = fg.get(sid, {})
    lines = [
        f"  {sid} | {s.get('name')} | {s.get('city', '')}, {s.get('country_name') or s.get('country', '')}",
        f"    lead_time_days={s.get('lead_time_days')}, commodities={s.get('commodities', [])}",
        f"    risk_score={r.get('score', 'n/a'):.1f}/100"
        if r.get("score") is not None
        else "    risk_score=n/a",
    ]
    comp = r.get("components") or {}
    if comp:
        lines.append(
            f"    risk_components: country={comp.get('country_risk', 'n/a')}, "
            f"commodity={comp.get('commodity_risk', 'n/a')}, lead_time={comp.get('lead_time', 'n/a')}"
        )
    if f:
        lines.append(
            f"    fear/greed: fear={f.get('fear_index')}, greed={f.get('greed_index')}, "
            f"sentiment={f.get('sentiment_label')}, parts_exposure={f.get('part_exposure_weight')}%"
        )
        for d in (f.get("drivers") or [])[:4]:
            lines.append(f"      driver: {d}")
    return lines


def _sim_for_scenario(snapshot: dict[str, Any], scenario_id: str) -> list[str]:
    rows = [
        r
        for r in snapshot.get("sim_results") or []
        if r.get("scenario_id") == scenario_id
    ]
    if not rows:
        return []
    lines = [f"  Scenario {scenario_id} ({rows[0].get('scenario_name', '')}):"]
    for r in rows:
        m = r.get("metrics") or {}
        lines.append(
            f"    strategy={r.get('strategy_id')}: stockout_P={m.get('stockout_probability', 0):.0%}, "
            f"service_level={m.get('service_level_pct', 0):.1f}%, "
            f"recovery_days~{m.get('recovery_days_est', 'n/a')}, "
            f"lead_time_mult={m.get('lead_time_multiplier', 1)}"
        )
    return lines


def _part_recommendation(snapshot: dict[str, Any], part_id: str) -> list[str]:
    for rec in snapshot.get("recommendations") or []:
        if rec.get("part_id") != part_id:
            continue
        alloc = rec.get("allocation") or {}
        alloc_s = ", ".join(f"{k}: {v:.1%}" for k, v in sorted(alloc.items(), key=lambda x: -x[1]))
        rat = rec.get("rationale") or {}
        lines = [
            f"  Part {rec.get('part_name')} ({part_id})",
            f"    allocation_mode={rec.get('allocation_mode')}, primary={rec.get('primary_supplier_id')}",
            f"    allocation: {alloc_s}",
            f"    topsis primary rank={rat.get('topsis_rank')}, max_scenario_stockout={rat.get('max_scenario_stockout', 0):.0%}",
        ]
        for d in rat.get("drivers") or []:
            lines.append(f"    driver: {d}")
        for alt in rec.get("alternative_solutions") or []:
            lines.append(f"    action option: {alt}")
        sr = rec.get("supplier_risks") or {}
        if sr:
            lines.append(
                "    supplier_risks: "
                + ", ".join(f"{k}={v:.1f}" for k, v in sorted(sr.items(), key=lambda x: -x[1]))
            )
        return lines
    return []


def _tire_section(snapshot: dict[str, Any], suppliers: dict, risks: dict, fg: dict) -> list[str]:
    lines = ["TYRE / MRF / GULF (priority supply-chain storyline):"]
    brief = snapshot.get("tire_disruption_brief")
    if brief:
        lines.append(f"  stress_level={brief.get('stress_level')} | {brief.get('headline')}")
        lines.append(f"  summary: {brief.get('summary', '')}")
        for b in brief.get("bullets") or []:
            lines.append(f"  • {b}")
        mrf = brief.get("mrf_supplier") or {}
        if mrf:
            lines.extend(_format_supplier_dossier(mrf.get("id", "SUP-IN-TIRE"), suppliers, risks, fg))
        for g in brief.get("gulf_feedstock") or []:
            gid = g.get("id")
            if gid:
                lines.extend(_format_supplier_dossier(gid, suppliers, risks, fg))
        for nh in brief.get("news_hits") or []:
            lines.append(f"  headline_hit: {nh.get('title', '')[:100]}")
    else:
        for sid in ("SUP-IN-TIRE", "SUP-AE-GULF-CHEM", "SUP-SA-CARBON"):
            lines.extend(_format_supplier_dossier(sid, suppliers, risks, fg))

    lines.extend(_part_recommendation(snapshot, "PART-TIRE"))
    lines.extend(_sim_for_scenario(snapshot, "ME-GULF-TIRE"))
    lines.extend(_sim_for_scenario(snapshot, "RUBBER-SHOCK"))
    return lines


def _history_section(snapshot: dict[str, Any], limit: int = 5) -> list[str]:
    hist = snapshot.get("disruption_history") or {}
    incidents = hist.get("incidents") or []
    if not incidents:
        return []
    lines = ["DISRUPTION HISTORY (public / demo episodes):"]
    for inc in incidents[:limit]:
        lines.append(
            f"  [{inc.get('year')}] {inc.get('title')} ({inc.get('category')}) "
            f"scenario_link={inc.get('related_scenario_id')}"
        )
        for b in (inc.get("impact_bullets") or [])[:2]:
            lines.append(f"    • {b}")
        lesson = (inc.get("supply_chain_lesson") or "").strip().replace("\n", " ")
        if lesson:
            lines.append(f"    lesson: {lesson[:200]}")
    return lines


def _signals_section(snapshot: dict[str, Any], limit: int = 8) -> list[str]:
    sig = snapshot.get("command_signals") or {}
    signals = sig.get("signals") or []
    if not signals:
        return []
    lines = ["COMMAND SIGNALS (prioritized):"]
    for s in signals[:limit]:
        lines.append(
            f"  [{s.get('severity')}] {s.get('title')} — {(s.get('detail') or '')[:160]}"
        )
    return lines


def _news_section(snapshot: dict[str, Any], user_message: str, limit: int = 8) -> list[str]:
    news = snapshot.get("news_headlines") or []
    if not news:
        return []
    msg = user_message.lower()
    filtered = news
    if TIRE_KEYWORDS.search(user_message):
        filtered = [
            n
            for n in news
            if TIRE_KEYWORDS.search(f"{n.get('title', '')} {n.get('summary', '')}")
        ] or news
    elif any(k in msg for k in ("chip", "semi", "ecu")):
        filtered = [
            n
            for n in news
            if re.search(r"chip|semi|ecu", f"{n.get('title', '')} {n.get('summary', '')}", re.I)
        ] or news
    lines = ["INGESTED NEWS (from last analysis run):"]
    for n in filtered[:limit]:
        lines.append(
            f"  [{n.get('severity', 'n/a')}] {n.get('title', '')[:110]} — "
            f"{(n.get('summary') or '')[:120]}"
        )
    return lines


def build_snapshot_context(
    snapshot: dict[str, Any] | None,
    user_message: str = "",
) -> str:
    if not snapshot:
        return (
            "No analysis run loaded yet. Tell the user to click Run analysis on the "
            "home page or header, then ask again."
        )

    suppliers = _supplier_map(snapshot)
    risks = _risk_map(snapshot)
    fg = _fg_map(snapshot)
    msg = user_message or ""
    tire_focus = bool(TIRE_KEYWORDS.search(msg)) or bool(snapshot.get("tire_disruption_brief"))

    lines: list[str] = [
        f"RUN: run_id={snapshot.get('run_id', '')}, generated_at={snapshot.get('generated_at', '')}",
        f"data_health={snapshot.get('data_health', {})}",
    ]

    msil = fg.get("MARUTI-SZKI") or (snapshot.get("fear_greed") or {}).get("maruti_suzuki")
    if msil:
        lines.append(
            f"MSIL sentiment: fear={msil.get('fear_index')}, greed={msil.get('greed_index')}, "
            f"label={msil.get('sentiment_label')}"
        )
        for d in msil.get("drivers") or []:
            lines.append(f"  MSIL driver: {d}")

    if tire_focus or snapshot.get("tire_disruption_brief"):
        lines.extend(_tire_section(snapshot, suppliers, risks, fg))
    else:
        lines.append("TOP SUPPLIER RISKS (by score):")
        for r in sorted(
            snapshot.get("supplier_risks") or [],
            key=lambda x: x.get("score", 0),
            reverse=True,
        )[:8]:
            sid = r.get("id", "")
            lines.extend(_format_supplier_dossier(sid, suppliers, risks, fg))

    lines.extend(_signals_section(snapshot))
    lines.extend(_news_section(snapshot, msg))

    if not tire_focus:
        lines.extend(_part_recommendation(snapshot, "PART-TIRE"))

    worst = None
    for r in snapshot.get("sim_results") or []:
        p = (r.get("metrics") or {}).get("stockout_probability", 0)
        if worst is None or p > worst[0]:
            worst = (p, r.get("scenario_name"), r.get("scenario_id"), r.get("strategy_id"))
    if worst:
        lines.append(
            f"WORST SIM: stockout_P={worst[0]:.0%} under “{worst[1]}” ({worst[2]}, {worst[3]})"
        )

    lines.extend(_history_section(snapshot))

    for rec in (snapshot.get("recommendations") or [])[:6]:
        if rec.get("part_id") == "PART-TIRE" and tire_focus:
            continue
        alloc = rec.get("allocation") or {}
        if not alloc:
            continue
        top = max(alloc.items(), key=lambda x: x[1])
        lines.append(
            f"Other part {rec.get('part_name')}: primary_alloc {top[0]}={top[1]:.0%}, mode={rec.get('allocation_mode')}"
        )

    return "\n".join(lines)


def build_system_prompt(
    snapshot: dict[str, Any] | None,
    user_message: str = "",
    live_enrichment: str = "",
) -> str:
    ctx = build_snapshot_context(snapshot, user_message)
    live_block = f"\n\n{live_enrichment}" if live_enrichment else ""
    return f"""You are the Maruti Suzuki Supply Chain Assistant — a senior analyst for sourcing and plant logistics.

Your job is to CONNECT THE DOTS: use every relevant number, supplier name, allocation %, simulation stockout probability, fear/greed index, signal, history episode, and live headline in the CONTEXT below. Give actionable guidance teams can execute this week.

Response format (use these headings when answering risk/supplier questions):
1. **Situation** — what is happening, tied to named suppliers/parts/scenarios
2. **Key metrics** — bullet list with specific numbers from CONTEXT (risk scores, allocations, stockout P, lead times)
3. **Recommended actions** — 3–5 concrete steps (dual-source, alternate corridor, buffer stock, which supplier to call)
4. **What to watch** — triggers from news, scenarios, or fear/greed drivers

Rules:
- NEVER say "data not provided", "cannot quantify", or "specific metrics unavailable" if CONTEXT contains the answer — search CONTEXT first.
- For MRF / Gulf / tyre questions: use TYRE / MRF / GULF section, PART-TIRE allocation, ME-GULF-TIRE simulation, and Gulf supplier dossiers.
- Cite demo vs live: numbers from CONTEXT are from the command-center analysis run; Yahoo/Google lines are live web supplements.
- Do not lecture about "run analysis" if run_id is already in CONTEXT.
- Be direct and expert — no filler apologies. Max ~350 words unless user asks for a deep dive.
- End with one short line: demo POC — validate decisions against MSIL ERP/supplier systems before execution.

CONTEXT (analysis snapshot + ingested news):
{ctx}{live_block}
"""
