"""AI / ML model registry and live status for command center UI."""

from __future__ import annotations

import hashlib
from typing import Any

from backend.config.loader import _load_yaml
from backend.settings import settings

MSIL_PLANTS = "Gurgaon, Manesar, and Gujarat"
OEM_NAME = "Maruti Suzuki India Limited"


def _load_models_config() -> dict:
    return _load_yaml(settings.config_dir / "ai_models.yaml")


def _pseudo_metric(seed: str, lo: float, hi: float) -> float:
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    return round(lo + (h % 1000) / 1000 * (hi - lo), 3)


def _supplier_name(cfg: Any, sid: str) -> str:
    sup = next((s for s in cfg.suppliers if s.id == sid), None)
    return sup.name if sup else sid


def _top_suppliers(
    supplier_risks: dict[str, float], cfg: Any, n: int = 3
) -> list[tuple[str, str, float]]:
    ranked = sorted(supplier_risks.items(), key=lambda x: -x[1])[:n]
    return [(sid, _supplier_name(cfg, sid), sc) for sid, sc in ranked]


def _top_countries(country_risks: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    return sorted(country_risks.items(), key=lambda x: -x[1])[:n]


def _filter_news(
    news: list[dict],
    *,
    risk_types: set[str] | None = None,
    min_severity: int = 1,
    limit: int = 4,
) -> list[dict]:
    out: list[dict] = []
    for n in news:
        sev = int(n.get("severity") or 1)
        rt = (n.get("risk_type") or "general").lower()
        if sev < min_severity:
            continue
        if risk_types and rt not in risk_types and sev < 3:
            continue
        out.append(n)
    out.sort(key=lambda x: (-int(x.get("severity") or 1), x.get("title", "")))
    return out[:limit]


def _news_for_model(mid: str, news: list[dict]) -> list[dict]:
    filters: dict[str, tuple[set[str] | None, int]] = {
        "gnn-supply-risk": (
            {"logistics", "geopolitical", "sanctions", "supplier", "commodity"},
            2,
        ),
        "transformer-news-nlp": (None, 2),
        "fear-greed-sentiment": (None, 2),
        "monte-carlo-scenario": (
            {"logistics", "geopolitical", "sanctions", "supplier"},
            2,
        ),
        "topsis-mcdm-engine": ({"supplier", "sanctions", "logistics"}, 2),
        "digital-twin-sim": ({"logistics", "supplier"}, 2),
        "lstm-demand-forecast": ({"commodity", "general", "logistics"}, 1),
        "rl-allocation-agent": ({"supplier", "logistics"}, 2),
    }
    risk_types, min_sev = filters.get(mid, (None, 2))
    return _filter_news(news, risk_types=risk_types, min_severity=min_sev, limit=5)


def _news_items_payload(articles: list[dict]) -> list[dict]:
    return [
        {
            "title": (a.get("title") or "Untitled")[:200],
            "summary": (a.get("summary") or "")[:320],
            "severity": int(a.get("severity") or 1),
            "risk_type": a.get("risk_type") or "general",
        }
        for a in articles
    ]


def _signals_for_model(
    mid: str, signals: list[dict], limit: int = 3
) -> list[dict]:
    category_map = {
        "gnn-supply-risk": {"supplier", "geopolitical"},
        "transformer-news-nlp": {"news"},
        "monte-carlo-scenario": {"scenario"},
        "topsis-mcdm-engine": {"sourcing", "supplier"},
        "fear-greed-sentiment": {"supplier", "geopolitical", "news"},
        "digital-twin-sim": {"scenario", "supplier"},
        "lstm-demand-forecast": {"geopolitical", "news"},
        "rl-allocation-agent": {"sourcing"},
    }
    cats = category_map.get(mid, set())
    picked = [s for s in signals if s.get("category") in cats]
    if len(picked) < limit:
        seen = {s["id"] for s in picked}
        for s in signals:
            if s["id"] not in seen:
                picked.append(s)
            if len(picked) >= limit:
                break
    return picked[:limit]


def _build_run_context(
    cfg: Any,
    *,
    supplier_risks: dict[str, float],
    country_risks: dict[str, float],
    sim_results: list[dict],
    recs: list[dict],
    news: list[dict],
    command_signals: dict | None,
    scenario_insights: list[dict] | None,
    news_count: int,
) -> dict:
    signals = (command_signals or {}).get("signals") or []
    critical = (command_signals or {}).get("critical_count", 0)
    high = (command_signals or {}).get("high_count", 0)
    high_news = [n for n in news if int(n.get("severity") or 1) >= 3]

    worst_sim = None
    if sim_results:
        worst_sim = max(
            sim_results,
            key=lambda r: r.get("metrics", {}).get("stockout_probability", 0),
        )

    single_source = [r for r in recs if r.get("allocation_mode") == "single_source"]

    return {
        "oem": OEM_NAME,
        "plants": MSIL_PLANTS,
        "supplier_count": len(cfg.suppliers),
        "part_count": len(cfg.parts),
        "avg_supplier": (
            sum(supplier_risks.values()) / len(supplier_risks) if supplier_risks else 0
        ),
        "avg_country": (
            sum(country_risks.values()) / len(country_risks) if country_risks else 0
        ),
        "top_suppliers": _top_suppliers(supplier_risks, cfg),
        "top_countries": _top_countries(country_risks),
        "news_count": news_count or len(news),
        "high_news_count": len(high_news),
        "signals": signals,
        "critical_signals": critical,
        "high_signals": high,
        "rec_count": len(recs),
        "single_source_count": len(single_source),
        "sim_count": len(sim_results),
        "worst_sim": worst_sim,
        "scenario_insights": scenario_insights or [],
        "recs_sample": recs[:3],
    }


def _facts_for_model(mid: str, ctx: dict, cfg: Any, supplier_risks: dict[str, float]) -> list[str]:
    facts: list[str] = []
    facts.append(
        f"{ctx['oem']} tracks {ctx['part_count']} parts and {ctx['supplier_count']} suppliers "
        f"in this demo network (plants: {ctx['plants']})."
    )

    if ctx["top_suppliers"]:
        top = ctx["top_suppliers"][0]
        facts.append(
            f"Highest supplier risk this run: {top[1]} ({top[0]}) at {top[2]:.1f}/100."
        )

    if ctx["top_countries"]:
        c0, s0 = ctx["top_countries"][0]
        facts.append(f"Top country exposure: {c0} at {s0:.1f}/100 on the country risk index.")

    facts.append(
        f"Command center flagged {ctx['critical_signals']} critical and "
        f"{ctx['high_signals']} high-priority signals in the latest run."
    )

    if mid == "gnn-supply-risk":
        facts.append(
            f"Network average supplier risk is {ctx['avg_supplier']:.1f}/100 — "
            "the graph model uses this to weight cascade paths across the BOM."
        )
    elif mid == "transformer-news-nlp":
        facts.append(
            f"{ctx['news_count']} headlines ingested; {ctx['high_news_count']} rated severity 3+ "
            "for supply-chain themes."
        )
    elif mid == "monte-carlo-scenario" and ctx["worst_sim"]:
        m = ctx["worst_sim"].get("metrics", {})
        facts.append(
            f"Stressed scenario “{ctx['worst_sim'].get('scenario_name', 'stress')}”: "
            f"stockout probability up to {m.get('stockout_probability', 0):.0%} in the matrix."
        )
    elif mid == "topsis-mcdm-engine":
        facts.append(f"{ctx['rec_count']} parts received fresh dual-source / allocation rankings.")
        if ctx["single_source_count"]:
            facts.append(
                f"{ctx['single_source_count']} parts still show single-source exposure in recommendations."
            )
    elif mid == "fear-greed-sentiment":
        facts.append(
            f"Sentiment blend uses {len(ctx.get('top_suppliers', []))} supplier risk nodes and "
            f"{len(ctx.get('top_countries', []))} country indices from this run."
        )
    elif mid == "digital-twin-sim":
        facts.append(
            f"Digital twin covers three MSIL manufacturing hubs with discrete-event routing "
            f"for {ctx['part_count']} configured parts."
        )
    elif mid == "lstm-demand-forecast":
        facts.append(
            "Forecast horizon targets the top 20 critical parts that gate line speed at MSIL plants."
        )
    elif mid == "rl-allocation-agent":
        facts.append(
            "Live PO splits still follow TOPSIS rankings while the RL policy trains in sandbox mode."
        )

    for sig in _signals_for_model(mid, ctx["signals"], limit=2):
        facts.append(f"Signal: {sig.get('title')} — {sig.get('detail', '')[:120]}")

    return facts[:6]


def _msil_why_for_model(mid: str, narr: dict, ctx: dict, live_note: str | None) -> str:
    base = (narr.get("how_it_helps") or "").strip()
    paragraphs = []

    if base:
        paragraphs.append(base)

    lead = (
        f"For {ctx['oem']}, every hour of avoidable downtime at {ctx['plants']} translates into "
        "lost retail deliveries and dealer stock pressure across India. This model turns raw "
        "pipeline data into decisions sourcing and plant teams can act on before lines slow down."
    )
    paragraphs.append(lead)

    if live_note:
        paragraphs.append(f"Right now: {live_note}")

    if mid == "gnn-supply-risk" and ctx["top_suppliers"]:
        names = ", ".join(t[1] for t in ctx["top_suppliers"][:2])
        paragraphs.append(
            f"When cascade risk rises through suppliers such as {names}, MSIL buyers can pre-build "
            "alternates or buffer stock for the exact BOM nodes the graph flags — instead of reacting "
            "after a tier-2 shock hits the news."
        )
    elif mid == "transformer-news-nlp":
        paragraphs.append(
            "Maruti’s command center does not have room to read every wire story. This model is the "
            "filter that tells plant and procurement leads which headlines actually touch logistics, "
            "sanctions, or supplier names in your configured network."
        )
    elif mid == "monte-carlo-scenario" and ctx["worst_sim"]:
        paragraphs.append(
            f"The latest stress test suggests scenarios where service levels slip — leadership can "
            f"see stockout odds before approving single-source savings on high-criticality parts."
        )
    elif mid == "topsis-mcdm-engine" and ctx["recs_sample"]:
        sample = ctx["recs_sample"][0]
        paragraphs.append(
            f"Example: part “{sample.get('part_name', sample.get('part_id'))}” now has a documented "
            "ranked supplier order tied to cost, risk, and lead time — the kind of audit trail "
            "committees expect when approving dual sourcing."
        )
    elif mid == "fear-greed-sentiment":
        paragraphs.append(
            "A single ‘fear’ reading on the dashboard gives the CEO and COO a shared vocabulary with "
            "finance and sourcing — especially when macro headlines (rupee, oil, trade) collide with "
            "supplier scorecards."
        )
    elif mid == "digital-twin-sim":
        paragraphs.append(
            "Plant heads can rehearse buffer and routing changes on the twin before risking real "
            "OEE at Gurgaon or Manesar — critical when a bottleneck part also appears in news alerts."
        )

    if ctx["critical_signals"] > 0:
        paragraphs.append(
            f"This run raised {ctx['critical_signals']} critical command signal(s) — this model’s "
            "output should be read alongside those alerts on the command center home page."
        )

    return "\n\n".join(paragraphs)


def _today_story(mid: str, live_note: str | None, ctx: dict) -> str:
    if live_note:
        prefix = {
            "gnn-supply-risk": "Today's network scan: ",
            "lstm-demand-forecast": "Latest forecast run: ",
            "transformer-news-nlp": "News desk update: ",
            "rl-allocation-agent": "Training log: ",
            "digital-twin-sim": "Twin snapshot: ",
            "topsis-mcdm-engine": "Sourcing desk: ",
            "monte-carlo-scenario": "Scenario lab: ",
            "fear-greed-sentiment": "Sentiment desk: ",
        }.get(mid, "Latest: ")
        return prefix + live_note

    return (
        f"No model-specific alert this run. Fleet context: average supplier risk "
        f"{ctx['avg_supplier']:.1f}, {ctx['news_count']} headlines processed."
    )


def _build_model_report(
    m: dict,
    live_note: str | None,
    ctx: dict,
    cfg: Any,
    supplier_risks: dict[str, float],
    news: list[dict],
) -> dict:
    narr = m.get("narrative") or {}
    mid = m["id"]
    today = _today_story(mid, live_note, ctx)
    facts = _facts_for_model(mid, ctx, cfg, supplier_risks)
    msil_why = _msil_why_for_model(mid, narr, ctx, live_note)
    model_news = _news_for_model(mid, news)
    news_body = ""
    if not model_news:
        news_body = (
            "No high-severity supply-chain headlines matched this model in the latest ingest. "
            "Lower-severity general news may still appear in the command center ticker."
        )

    inputs = m.get("inputs") or []
    outputs = m.get("outputs") or []

    sections: list[dict] = [
        {
            "title": "In plain English",
            "body": narr.get("plain_english") or m.get("description", ""),
        },
        {"title": "Today's brief", "body": today},
        {
            "title": "Facts from this run",
            "body": "Numbers and signals pulled from the latest analysis pipeline:",
            "bullets": facts,
        },
        {
            "title": "In the news",
            "body": news_body,
            "news_items": _news_items_payload(model_news),
        },
        {
            "title": "Why it matters for Maruti Suzuki",
            "body": msil_why,
        },
        {
            "title": "What to watch",
            "body": narr.get("watch_for")
            or "Sudden confidence drops or drift flags on this card.",
        },
        {
            "title": "Technical footnote",
            "body": (
                f"Reads: {', '.join(inputs) or 'pipeline feeds'}. "
                f"Produces: {', '.join(outputs) or 'scores and ranks'}."
            ),
        },
    ]

    return {
        "headline": narr.get("headline") or m.get("name", "Model brief"),
        "lede": narr.get("lede") or m.get("description", ""),
        "sections": sections,
    }


def build_ai_models_payload(
    cfg: Any,
    *,
    supplier_risks: dict[str, float] | None = None,
    country_risks: dict[str, float] | None = None,
    sim_results: list[dict] | None = None,
    recs: list[dict] | None = None,
    news: list[dict] | None = None,
    news_count: int = 0,
    run_id: str | None = None,
    command_signals: dict | None = None,
    scenario_insights: list[dict] | None = None,
) -> dict:
    raw = _load_models_config()
    models_cfg = raw.get("models", [])
    supplier_risks = supplier_risks or {}
    country_risks = country_risks or {}
    sim_results = sim_results or []
    recs = recs or []
    news = news or []
    seed_base = run_id or "baseline"

    avg_supplier = (
        sum(supplier_risks.values()) / len(supplier_risks) if supplier_risks else 42.0
    )
    avg_country = (
        sum(country_risks.values()) / len(country_risks) if country_risks else 38.0
    )
    worst_stockout = max(
        (r.get("metrics", {}).get("stockout_probability", 0) for r in sim_results),
        default=0.15,
    )

    run_ctx = _build_run_context(
        cfg,
        supplier_risks=supplier_risks,
        country_risks=country_risks,
        sim_results=sim_results,
        recs=recs,
        news=news,
        command_signals=command_signals,
        scenario_insights=scenario_insights,
        news_count=news_count or len(news),
    )

    models: list[dict] = []
    for m in models_cfg:
        mid = m["id"]
        conf = _pseudo_metric(f"{seed_base}:{mid}:conf", 0.72, 0.96)
        drift = _pseudo_metric(f"{seed_base}:{mid}:drift", 0.01, 0.12)
        last_trained = "2026-05-10" if m.get("status") == "active" else "2026-04-22"

        live_note = None
        if mid == "gnn-supply-risk" and supplier_risks:
            top = max(supplier_risks, key=supplier_risks.get)
            live_note = (
                f"Elevated cascade risk via {top} "
                f"({_supplier_name(cfg, top)}, score {supplier_risks[top]:.1f})"
            )
        elif mid == "monte-carlo-scenario" and sim_results:
            live_note = (
                f"{len(sim_results)} strategy paths evaluated; "
                f"max stockout P={worst_stockout:.0%}"
            )
        elif mid == "transformer-news-nlp":
            live_note = f"{news_count or len(news)} headlines ingested in last run"
        elif mid == "topsis-mcdm-engine" and recs:
            live_note = f"{len(recs)} part-level allocation recommendations active"
        elif mid == "fear-greed-sentiment":
            live_note = (
                f"Blending {len(supplier_risks)} supplier + "
                f"{len(country_risks)} country signals"
            )
        elif mid == "lstm-demand-forecast":
            live_note = "Top-20 critical parts: next 8-week horizon refreshed"
        elif mid == "rl-allocation-agent":
            live_note = "Policy replay in sandbox — not yet wired to live PO splits"
        elif mid == "digital-twin-sim":
            live_note = "Gurgaon · Manesar · Gujarat twins synced to baseline routing"

        report = _build_model_report(
            m, live_note, run_ctx, cfg, supplier_risks, news
        )

        models.append(
            {
                **m,
                "confidence": conf,
                "drift_score": drift,
                "last_trained": last_trained,
                "live_note": live_note,
                "health": "healthy" if drift < 0.08 else "watch",
                "report": report,
            }
        )

    active = sum(1 for m in models if m.get("status") == "active")
    training = sum(1 for m in models if m.get("status") == "training")

    return {
        "disclaimer": raw.get("disclaimer", ""),
        "summary": {
            "total_models": len(models),
            "active": active,
            "training": training,
            "avg_confidence": round(
                sum(m["confidence"] for m in models) / max(len(models), 1), 3
            ),
            "fleet_health": (
                "optimal" if avg_supplier < 55 and worst_stockout < 0.35 else "elevated"
            ),
            "avg_supplier_risk": round(avg_supplier, 1),
            "avg_country_risk": round(avg_country, 1),
        },
        "models": models,
        "pipelines": [
            {
                "id": "ingest-enrich",
                "name": "Ingest → Enrich → Score",
                "stages": ["FRED", "World Bank", "GDELT/RSS", "Risk engine", "MCDM"],
                "status": "live",
            },
            {
                "id": "simulate-decide",
                "name": "Simulate → Recommend → Act",
                "stages": ["Scenario MC", "RL allocator", "Human-in-loop"],
                "status": "live" if sim_results else "idle",
            },
        ],
    }
