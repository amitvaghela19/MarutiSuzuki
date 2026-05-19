import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any

from backend.analytics.mcdm.engine import run_mcdm
from backend.analytics.fear_greed import build_fear_greed_indices
from backend.analytics.sourcing import build_sourcing_matrix
from backend.utils.countries import country_name
from backend.config.loader import load_strategic_raw
from backend.utils.strategic import normalize_strategic_payload
from backend.analytics.ai_hub import build_ai_models_payload
from backend.analytics.command_signals import build_command_signals
from backend.analytics.disruption_history import build_disruption_history_payload
from backend.analytics.tire_brief import build_tire_disruption_brief
from backend.analytics.digital_twin import build_digital_twin
from backend.analytics.part_catalog import build_enriched_parts_catalog
from backend.analytics.recommendations import build_recommendations
from backend.analytics.risk import score_commodities, score_countries, score_suppliers
from backend.analytics.simulation import build_scenario_insights, run_scenarios
from backend.config.loader import load_config
from backend.db.repository import Repository
from backend.ingestion.orchestrator import run_ingestion
from backend.settings import settings


def _build_snapshot(
    run_id: str,
    cfg: Any,
    ingest: dict,
    news: list,
    country_risk: list,
    commodity_risk: list,
    supplier_risk: list,
    mcdm_rows: list,
    part_ranks: dict,
    sim_results: list,
    recs: list,
    data_health: dict,
    rank_stability: dict,
    news_count: int = 0,
) -> dict:
    supplier_map = {sid: sc for sid, sc, _ in supplier_risk}
    country_map = {c: sc for c, sc, _ in country_risk}
    scenario_insights = build_scenario_insights(cfg, sim_results)
    commodity_map = {c: sc for c, sc, _ in commodity_risk}
    disruption_history = build_disruption_history_payload(
        sim_results=sim_results,
        commodity_risks=commodity_map,
    )
    tire_disruption_brief = build_tire_disruption_brief(
        cfg,
        supplier_risks=supplier_map,
        country_risks=country_map,
        news=news,
        sim_results=sim_results,
    )
    command_signals = build_command_signals(
        cfg,
        news=news,
        country_risk=country_risk,
        supplier_risk=supplier_risk,
        recs=recs,
        sim_results=sim_results,
        tire_brief=tire_disruption_brief,
    )
    return {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_health": data_health,
        "country_risks": [
            {
                "code": c,
                "name": country_name(c),
                "score": s,
                "components": comp,
            }
            for c, s, comp in country_risk
        ],
        "commodity_risks": [
            {"id": c, "score": s, "components": comp} for c, s, comp in commodity_risk
        ],
        "supplier_risks": [
            {"id": sid, "score": s, "components": comp} for sid, s, comp in supplier_risk
        ],
        "news_count": news_count or len(news),
        "news_headlines": news[:10],
        "mcdm": mcdm_rows,
        "part_rankings": part_ranks,
        "rank_stability": rank_stability,
        "sim_results": sim_results,
        "scenario_insights": scenario_insights,
        "recommendations": recs,
        "suppliers": [
            {**s.model_dump(), "country_name": country_name(s.country)} for s in cfg.suppliers
        ],
        "parts": [p.model_dump() for p in cfg.parts],
        "parts_by_category": _parts_by_category(cfg),
        "company": cfg.company.model_dump() if cfg.company else None,
        "strategic": normalize_strategic_payload(load_strategic_raw())
        if load_strategic_raw()
        else {},
        "sourcing_matrix": build_sourcing_matrix(
            cfg,
            supplier_risks={sid: sc for sid, sc, _ in supplier_risk},
            recommendations=recs,
        ),
        "fear_greed": build_fear_greed_indices(
            cfg,
            supplier_risks={sid: sc for sid, sc, _ in supplier_risk},
            supplier_components={sid: comp for sid, _, comp in supplier_risk},
            country_risks={c: sc for c, sc, _ in country_risk},
            commodity_risks={c: sc for c, sc, _ in commodity_risk},
            news=news,
            sim_results=sim_results,
        ),
        "ai_models": build_ai_models_payload(
            cfg,
            supplier_risks=supplier_map,
            country_risks=country_map,
            sim_results=sim_results,
            recs=recs,
            news=news,
            news_count=news_count or len(news),
            run_id=run_id,
            command_signals=command_signals,
            scenario_insights=scenario_insights,
        ),
        "digital_twin": build_digital_twin(cfg, supplier_risks=supplier_map, run_id=run_id),
        "command_signals": command_signals,
        "parts_catalog_enriched": build_enriched_parts_catalog(
            cfg,
            supplier_risks=supplier_map,
            supplier_components={sid: comp for sid, _, comp in supplier_risk},
            recommendations=recs,
            part_rankings=part_ranks,
        ),
        "disruption_history": disruption_history,
        "tire_disruption_brief": tire_disruption_brief,
    }


def _parts_by_category(cfg: Any) -> dict[str, list]:
    out: dict[str, list] = {}
    for p in cfg.parts:
        out.setdefault(p.category, []).append(p.model_dump())
    return out


def _compute_analysis(
    cfg: Any,
    repo: Repository,
    run_id: str,
    ingest_bundle: dict,
    news: list,
) -> dict:
    """CPU/DB-heavy phase — run off the event loop via asyncio.to_thread."""
    country_risk = score_countries(cfg, ingest_bundle, news)
    commodity_risk = score_commodities(cfg, ingest_bundle, news)
    country_map = {c: s for c, s, _ in country_risk}
    commodity_map = {c: s for c, s, _ in commodity_risk}
    supplier_risk = score_suppliers(cfg, country_map, commodity_map)

    repo.bulk_insert_risks(run_id, "country_risk", country_risk, "country_code")
    repo.bulk_insert_risks(run_id, "commodity_risk", commodity_risk, "commodity_id")
    repo.bulk_insert_risks(run_id, "supplier_risk", supplier_risk, "supplier_id")

    supplier_map = {s: sc for s, sc, _ in supplier_risk}
    mcdm_rows: list[dict] = []
    part_ranks: dict[str, dict[str, int]] = {}
    rank_stability: dict[str, bool] = {}

    for part in cfg.parts:
        rows, ranks, stable = run_mcdm(cfg, part.id, part.supplier_ids, country_map, supplier_map)
        mcdm_rows.extend(rows)
        part_ranks[part.id] = ranks
        rank_stability[part.id] = stable

    repo.insert_mcdm(run_id, mcdm_rows)

    sim_results = run_scenarios(cfg, supplier_map)
    for r in sim_results:
        r["run_id"] = run_id
    repo.insert_sim_results(run_id, sim_results)

    recs = build_recommendations(cfg, part_ranks, supplier_map, sim_results)
    repo.insert_recommendations(run_id, recs)

    data_health = ingest_bundle.get("health", {})
    repo.finish_run(run_id, data_health)

    snapshot = _build_snapshot(
        run_id,
        cfg,
        ingest_bundle,
        news,
        country_risk,
        commodity_risk,
        supplier_risk,
        mcdm_rows,
        part_ranks,
        sim_results,
        recs,
        data_health,
        rank_stability,
        news_count=len(news),
    )

    settings.snapshots_dir.mkdir(parents=True, exist_ok=True)
    path = settings.snapshots_dir / f"{run_id}.json"
    path.write_text(json.dumps(snapshot, default=str, indent=2), encoding="utf-8")
    latest = settings.snapshots_dir / "latest.json"
    latest.write_text(json.dumps(snapshot, default=str, indent=2), encoding="utf-8")

    return snapshot


async def run_full_analysis() -> dict:
    cfg = load_config()
    repo = Repository()
    run_id = str(uuid4())
    repo.start_run(run_id)
    repo.sync_config_entities(cfg)

    ingest_bundle, news = await run_ingestion(cfg, repo)
    repo.insert_news(run_id, news)

    return await asyncio.to_thread(
        _compute_analysis, cfg, repo, run_id, ingest_bundle, news
    )
