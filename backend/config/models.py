from typing import Any

from pydantic import BaseModel, Field


class CountryRef(BaseModel):
    code: str
    name: str


class CommoditySeries(BaseModel):
    id: str
    name: str
    fred_series: str | None = None
    unit: str | None = None


class WorldBankIndicator(BaseModel):
    id: str
    name: str


class DataSourcesConfig(BaseModel):
    countries: list[CountryRef]
    worldbank_indicators: list[WorldBankIndicator] = Field(default_factory=list)
    commodity_series: list[CommoditySeries] = Field(default_factory=list)
    gdelt_queries: list[str] = Field(default_factory=list)
    rss_feeds: list[str] = Field(default_factory=list)


class SupplierConfig(BaseModel):
    id: str
    name: str
    country: str
    commodities: list[str] = Field(default_factory=list)
    cost_index: float = 1.0
    lead_time_days: int = 14
    capability_flags: dict[str, bool] = Field(default_factory=dict)
    city: str = ""
    trust_tier: str = "oem_tier1"
    discovery_source: str = ""
    indiamart_category: str = ""
    reference_url: str | None = None


class PartConfig(BaseModel):
    id: str
    name: str
    category: str = "general"
    vehicle_system: str = ""
    criticality: int = 3
    main_commodity: str = ""
    supplier_ids: list[str] = Field(default_factory=list)
    primary_supplier_id: str | None = None
    alternative_solutions: list[str] = Field(default_factory=list)


class PlantConfig(BaseModel):
    id: str
    name: str
    location: str
    parts_used: list[str] = Field(default_factory=list)


class McdmCriterion(BaseModel):
    id: str
    name: str
    direction: str = "min"  # min = lower is better, max = higher is better
    weight: float | None = None


class McdmConfig(BaseModel):
    criteria: list[McdmCriterion]
    ahp_pairwise: list[list[float]] | None = None
    gates: dict[str, Any] = Field(default_factory=dict)


class ThresholdsConfig(BaseModel):
    high_risk: float = 70.0
    emergency_override: float = 85.0
    stockout_probability_limit: float = 0.25
    dual_source_split: list[float] = Field(default_factory=lambda: [0.6, 0.4])


class ScenarioConfig(BaseModel):
    id: str
    name: str
    description: str = ""
    severity: str = "medium"
    category: str = "general"
    duration_days: int = 30
    shock: dict[str, Any] = Field(default_factory=dict)


class NewsKeywordRule(BaseModel):
    keywords: list[str]
    severity: int = 2
    risk_type: str = "general"
    country_hints: list[str] = Field(default_factory=list)


class NewsKeywordsConfig(BaseModel):
    rules: list[NewsKeywordRule] = Field(default_factory=list)


class CompanyProfile(BaseModel):
    name: str
    ticker: str = ""
    reference_url: str | None = None
    tagline: str = ""
    parent_group: str = ""
    founded: int | str = ""
    headquarters: str = ""
    role: str = ""
    business_model: list[str] = Field(default_factory=list)
    manufacturing_footprint: list[dict[str, Any]] = Field(default_factory=list)
    product_highlights: list[str] = Field(default_factory=list)
    supply_chain_themes: list[str] = Field(default_factory=list)
    key_metrics_demo: dict[str, Any] = Field(default_factory=dict)
    disclaimer: str = ""


class PartnerAnalysis(BaseModel):
    id: str
    name: str
    relationship: str = ""
    swot_summary: dict[str, list[Any]] = Field(default_factory=dict)
    pestle_highlights: dict[str, list[Any]] = Field(default_factory=dict)


class StrategicAnalysisConfig(BaseModel):
    maruti_suzuki: dict[str, Any] = Field(default_factory=dict)
    partners: list[PartnerAnalysis] = Field(default_factory=list)


class AppConfig(BaseModel):
    suppliers: list[SupplierConfig]
    parts: list[PartConfig]
    plants: list[PlantConfig]
    mcdm: McdmConfig
    thresholds: ThresholdsConfig
    scenarios: list[ScenarioConfig]
    data_sources: DataSourcesConfig
    news_keywords: NewsKeywordsConfig
    company: CompanyProfile | None = None
    strategic: StrategicAnalysisConfig | None = None
