from fastapi import APIRouter

from backend.analytics.fear_greed import build_fear_greed_indices
from backend.analytics.part_catalog import build_enriched_parts_catalog
from backend.analytics.simulation import build_scenario_insights
from backend.analytics.sourcing import build_sourcing_matrix
from backend.utils.supplier_strategic import (
    load_supplier_strategic_raw,
    normalize_supplier_strategic_payload,
)
from backend.config.loader import _load_yaml, load_config, load_strategic_raw
from backend.settings import settings
from backend.utils.countries import country_name
from backend.utils.strategic import normalize_strategic_payload

router = APIRouter(tags=["company"])


@router.get("/company/profile")
def company_profile():
    cfg = load_config()
    if not cfg.company:
        return {"error": "Company profile not configured"}
    return cfg.company.model_dump()


@router.get("/company/strategic")
def strategic_analysis():
    raw = load_strategic_raw()
    if not raw:
        return {"error": "Strategic analysis not configured"}
    payload = normalize_strategic_payload(raw)
    sup_raw = load_supplier_strategic_raw()
    if sup_raw.get("suppliers"):
        payload["supplier_strategic"] = normalize_supplier_strategic_payload(sup_raw)
    return payload


@router.get("/parts/catalog")
def parts_catalog():
    cfg = load_config()
    by_category: dict[str, list] = {}
    for p in cfg.parts:
        by_category.setdefault(p.category, []).append(p.model_dump())
    return {
        "total": len(cfg.parts),
        "categories": list(by_category.keys()),
        "parts": [p.model_dump() for p in cfg.parts],
        "by_category": by_category,
    }


@router.get("/parts/catalog/enriched")
def parts_catalog_enriched():
    import json

    from backend.settings import settings

    cfg = load_config()
    supplier_risks: dict[str, float] | None = None
    supplier_components: dict[str, dict] | None = None
    recommendations: list | None = None
    part_rankings: dict | None = None
    path = settings.snapshots_dir / "latest.json"
    if path.exists():
        snap = json.loads(path.read_text(encoding="utf-8"))
        supplier_risks = {s["id"]: s["score"] for s in snap.get("supplier_risks", [])}
        supplier_components = {
            s["id"]: s.get("components", {}) for s in snap.get("supplier_risks", [])
        }
        recommendations = snap.get("recommendations")
        part_rankings = snap.get("part_rankings")
    return build_enriched_parts_catalog(
        cfg,
        supplier_risks=supplier_risks,
        supplier_components=supplier_components,
        recommendations=recommendations,
        part_rankings=part_rankings,
    )


@router.get("/suppliers/strategic")
def suppliers_strategic():
    raw = load_supplier_strategic_raw()
    if not raw.get("suppliers"):
        return {"error": "Supplier strategic profiles not configured", "suppliers": []}
    return normalize_supplier_strategic_payload(raw)


@router.get("/sourcing/matrix")
def sourcing_matrix():
    cfg = load_config()
    return build_sourcing_matrix(cfg)


@router.get("/suppliers/catalog")
def suppliers_catalog():
    cfg = load_config()
    trust_raw = _load_yaml(settings.config_dir / "supplier_trust.yaml")
    return {
        "total": len(cfg.suppliers),
        "disclaimer": (
            "Demo supplier directory — names are illustrative. IndiaMART links are public "
            "category pages for trusted discovery, not vendor endorsements."
        ),
        "trust_tiers": trust_raw.get("trust_tiers", {}),
        "indiamart_note": trust_raw.get("indiamart_note", ""),
        "suppliers": [
            {**s.model_dump(), "country_name": country_name(s.country)} for s in cfg.suppliers
        ],
    }


@router.get("/scenarios/catalog")
def scenarios_catalog():
    cfg = load_config()
    empty_insights = build_scenario_insights(cfg, [])
    return {
        "catalog": empty_insights["catalog"],
        "strategy_legend": empty_insights["strategy_legend"],
        "disclaimer": empty_insights["disclaimer"],
    }


@router.get("/sentiment/fear-greed")
def fear_greed_index():
    """Fear & Greed indices for Maruti Suzuki and each supplier (config baseline if no run)."""
    cfg = load_config()
    return build_fear_greed_indices(cfg)
