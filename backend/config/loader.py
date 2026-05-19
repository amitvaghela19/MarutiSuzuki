from pathlib import Path

import yaml

from backend.config.models import (
    AppConfig,
    CompanyProfile,
    DataSourcesConfig,
    McdmConfig,
    NewsKeywordsConfig,
    PartConfig,
    PlantConfig,
    PartnerAnalysis,
    ScenarioConfig,
    StrategicAnalysisConfig,
    SupplierConfig,
    ThresholdsConfig,
)
from backend.settings import settings


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_strategic_raw(config_dir: Path | None = None) -> dict:
    base = config_dir or settings.config_dir
    return _load_yaml(base / "strategic_analysis.yaml")


def load_config(config_dir: Path | None = None) -> AppConfig:
    base = config_dir or settings.config_dir
    suppliers = [SupplierConfig(**s) for s in _load_yaml(base / "suppliers.yaml").get("suppliers", [])]
    parts_raw = _load_yaml(base / "parts.yaml").get("parts", [])
    parts_extra = _load_yaml(base / "parts_extra.yaml").get("parts", [])
    parts = [PartConfig(**p) for p in parts_raw + parts_extra]
    plants = [PlantConfig(**p) for p in _load_yaml(base / "plants.yaml").get("plants", [])]
    mcdm = McdmConfig(**_load_yaml(base / "mcdm.yaml"))
    thresholds = ThresholdsConfig(**_load_yaml(base / "thresholds.yaml"))
    scenarios = [ScenarioConfig(**s) for s in _load_yaml(base / "scenarios.yaml").get("scenarios", [])]
    data_sources = DataSourcesConfig(**_load_yaml(base / "data_sources.yaml"))
    news_keywords = NewsKeywordsConfig(**_load_yaml(base / "news_keywords.yaml"))
    company_raw = _load_yaml(base / "maruti_company.yaml").get("company", {})
    company = CompanyProfile(**company_raw) if company_raw else None
    strat_raw = _load_yaml(base / "strategic_analysis.yaml")
    strategic = None
    if strat_raw:
        partners = []
        for p in strat_raw.get("partners", []):
            partners.append(
                PartnerAnalysis(
                    id=p["id"],
                    name=p["name"],
                    relationship=p.get("relationship", ""),
                    swot_summary=p.get("swot_summary") or {},
                    pestle_highlights=p.get("pestle_highlights") or {},
                )
            )
        strategic = StrategicAnalysisConfig(
            maruti_suzuki=strat_raw.get("maruti_suzuki", {}),
            partners=partners,
        )
    return AppConfig(
        suppliers=suppliers,
        parts=parts,
        plants=plants,
        mcdm=mcdm,
        thresholds=thresholds,
        scenarios=scenarios,
        data_sources=data_sources,
        news_keywords=news_keywords,
        company=company,
        strategic=strategic,
    )
