export type CompanyProfile = {
  name: string;
  ticker?: string;
  tagline?: string;
  parent_group?: string;
  founded?: number | string;
  headquarters?: string;
  role?: string;
  business_model?: string[];
  manufacturing_footprint?: { name: string; focus: string }[];
  product_highlights?: string[];
  supply_chain_themes?: string[];
  key_metrics_demo?: Record<string, unknown>;
  disclaimer?: string;
};

export type CitedBullet = {
  text: string;
  source_url?: string | null;
  source_label?: string | null;
};

export type StrategicPayload = {
  sources_note?: string;
  supplier_strategic?: SupplierStrategicPayload;
  maruti_suzuki: {
    swot?: Record<string, CitedBullet[]>;
    pestle?: Record<string, CitedBullet[]>;
  };
  partners: {
    id: string;
    name: string;
    relationship?: string;
    swot_summary?: Record<string, CitedBullet[]>;
    pestle_highlights?: Record<string, CitedBullet[]>;
  }[];
};

export type PartRow = {
  id: string;
  name: string;
  category: string;
  vehicle_system?: string;
  criticality: number;
  main_commodity: string;
  supplier_ids: string[];
  primary_supplier_id?: string;
  alternative_solutions?: string[];
};

export type EnrichedPartSupplier = {
  id: string;
  name: string;
  country: string;
  country_name?: string;
  lead_time_days?: number;
  trust_tier?: string;
  is_primary: boolean;
  topsis_rank?: number;
  risk_score?: number | null;
  risk_components?: Record<string, number>;
  reference_url?: string | null;
};

export type EnrichedPartRow = PartRow & {
  suppliers: EnrichedPartSupplier[];
  supplier_count: number;
  composite_risk_score?: number | null;
  recommendation?: {
    part_id: string;
    part_name: string;
    allocation: Record<string, number>;
    rationale: Record<string, unknown>;
  } | null;
  why_summary: string;
};

export type PartsCatalogEnriched = {
  total: number;
  categories: string[];
  by_category: Record<string, EnrichedPartRow[]>;
  parts: EnrichedPartRow[];
};

export type SupplierStrategicProfile = {
  id: string;
  name: string;
  country: string;
  swot: Record<string, CitedBullet[]>;
  pestle: Record<string, CitedBullet[]>;
};

export type SupplierStrategicPayload = {
  disclaimer: string;
  total: number;
  suppliers: SupplierStrategicProfile[];
};

export type SourcingSupplierRef = {
  id: string;
  name: string;
  country: string;
  country_name?: string;
  lead_time_days: number;
  commodities?: string[];
  risk_score?: number;
};

export type SourcingPartRow = {
  part_id: string;
  part_name: string;
  category: string;
  vehicle_system: string;
  criticality: number;
  main_commodity: string;
  primary_supplier: SourcingSupplierRef | null;
  alternate_suppliers: SourcingSupplierRef[];
  alternative_solutions: string[];
  recommended_allocation?: Record<string, number> | null;
  allocation_mode?: string | null;
  allocation_rationale?: Record<string, unknown> | null;
};

export type SourcingMatrix = {
  disclaimer: string;
  parts: SourcingPartRow[];
  suppliers_index: {
    supplier: SourcingSupplierRef;
    primary_for_parts: { part_id: string; part_name: string }[];
    alternate_for_parts: { part_id: string; part_name: string }[];
  }[];
};

export type SupplierCatalogRow = {
  id: string;
  name: string;
  country: string;
  country_name?: string;
  city?: string;
  commodities?: string[];
  cost_index?: number;
  lead_time_days?: number;
  trust_tier?: string;
  discovery_source?: string;
  indiamart_category?: string;
  reference_url?: string | null;
  capability_flags?: Record<string, boolean>;
};

export type FearGreedEntity = {
  id: string;
  name: string;
  ticker?: string;
  country?: string;
  country_name?: string;
  fear_index: number;
  greed_index: number;
  sentiment_label: string;
  part_exposure_weight?: number;
  drivers?: string[];
  reference_url?: string | null;
};

export type SimStrategyRow = {
  scenario_id: string;
  scenario_name?: string;
  scenario_description?: string;
  severity?: string;
  category?: string;
  duration_days?: number;
  strategy_id: string;
  shock?: Record<string, unknown>;
  metrics: {
    avg_stockouts?: number;
    p90_stockouts?: number;
    stockout_probability: number;
    service_level_pct?: number;
    recovery_days_est?: number;
    relative_cost_index?: number;
    monte_carlo_runs?: number;
    [key: string]: number | undefined;
  };
};

export type ScenarioInsights = {
  disclaimer: string;
  monte_carlo_runs: number;
  catalog: {
    id: string;
    name: string;
    description: string;
    severity: string;
    category: string;
    duration_days: number;
    shock: Record<string, unknown>;
    related_history_id?: string;
    historical_analog?: string;
  }[];
  scenarios: {
    scenario_id: string;
    name: string;
    description: string;
    severity: string;
    category: string;
    duration_days: number;
    shock: Record<string, unknown>;
    recommended_strategy: string;
    recommendation_reason: string;
    dual_source_benefit: number;
    vs_baseline_stockout_delta: number;
    strategies: SimStrategyRow[];
    related_history_id?: string;
    historical_analog?: string;
  }[];
  heatmap: {
    scenario_id: string;
    strategy_id: string;
    stockout_probability: number;
    service_level_pct: number;
  }[];
  strategy_legend: Record<string, string>;
};

export type FearGreedBulletinDetail = {
  overview: string;
  fear_impact: string;
  greed_impact: string;
  msil_supply_chain: string;
  what_to_watch: string[];
  key_facts?: string[];
};

export type FearGreedBulletin = {
  id: string;
  kind: "news" | "driver" | "macro";
  title: string;
  teaser: string;
  severity?: number;
  severity_label?: string;
  risk_type?: string;
  country_code?: string;
  source_url?: string;
  source_label?: string;
  published_at?: string;
  detail: FearGreedBulletinDetail;
};

export type FearGreedPayload = {
  disclaimer: string;
  scale_note: string;
  maruti_suzuki: FearGreedEntity;
  suppliers: FearGreedEntity[];
  bulletins?: FearGreedBulletin[];
};

export type AIModelsPayload = {
  disclaimer: string;
  summary: {
    total_models: number;
    active: number;
    training: number;
    avg_confidence: number;
    fleet_health: string;
    avg_supplier_risk?: number;
    avg_country_risk?: number;
  };
  models: {
    id: string;
    name: string;
    family: string;
    version: string;
    status: string;
    description: string;
    confidence?: number;
    drift_score?: number;
    health?: string;
    live_note?: string | null;
    latency_ms?: number;
    accuracy_demo?: number;
    last_trained?: string;
    report?: {
      headline: string;
      lede: string;
      sections: {
        title: string;
        body: string;
        bullets?: string[];
        news_items?: {
          title: string;
          summary?: string;
          severity?: number;
          risk_type?: string;
        }[];
      }[];
    };
  }[];
  pipelines: { id: string; name: string; stages: string[]; status: string }[];
};

export type DigitalTwinPayload = {
  disclaimer: string;
  network_health: string;
  sensor_types?: string[];
  global_kpis: {
    total_plants: number;
    avg_oee_pct: number;
    plants_constrained: number;
  };
  plants: {
    id: string;
    name: string;
    location: string;
    metrics: {
      throughput_units_per_hour: number;
      buffer_days_of_supply: number;
      oee_pct: number;
      quality_ppm: number;
      energy_kwh_per_unit?: number;
      parts_on_line?: number;
      status: string;
    };
    bottlenecks: {
      part_id: string;
      part_name: string;
      supplier_id?: string;
      risk_score: number;
    }[];
    lines: { id: string; name: string; utilization_pct: number }[];
  }[];
};

export type CommandSignal = {
  id: string;
  priority: number;
  severity: string;
  category: string;
  title: string;
  detail: string;
  why?: string;
  summary?: string;
  risk_type?: string;
  news_index?: number;
  entity_id?: string | null;
  action: string;
  navigate_to?: string;
};

export type NewsHeadline = {
  title: string;
  severity?: number;
  risk_type?: string;
  summary?: string;
  country_code?: string;
  url?: string;
  published_at?: string;
};

export type CommandSignalsPayload = {
  total: number;
  critical_count: number;
  high_count: number;
  autopilot_mode: string;
  last_refresh_note: string;
  signals: CommandSignal[];
};

export type DisruptionIncident = {
  id: string;
  year: number;
  title: string;
  category: string;
  summary: string;
  impact_bullets?: string[];
  supply_chain_lesson?: string;
  related_scenario_id?: string | null;
  source_label?: string;
  source_url?: string;
  live_analog?: boolean;
};

export type DisruptionHistoryPayload = {
  disclaimer: string;
  incidents: DisruptionIncident[];
  timeline_summary: string;
  analog_count?: number;
};

export type TireDisruptionBrief = {
  disclaimer: string;
  part_id: string;
  part_name: string;
  stress_level: string;
  headline: string;
  summary: string;
  bullets: string[];
  mrf_supplier: { id: string; name: string; risk_score: number };
  gulf_feedstock: {
    id: string;
    name: string;
    country: string;
    risk_score: number;
  }[];
  gulf_country_scores: Record<string, number>;
  related_scenario_id?: string;
  related_history_id?: string;
  news_hits: { title: string; summary?: string; severity?: number }[];
  navigate_to?: string;
  navigate_part_id?: string;
};

export type Snapshot = {
  run_id: string;
  generated_at: string;
  data_health: Record<string, string>;
  country_risks: {
    code: string;
    name?: string;
    score: number;
    components: Record<string, number>;
  }[];
  commodity_risks: { id: string; score: number; components: Record<string, number> }[];
  supplier_risks: { id: string; score: number; components: Record<string, number> }[];
  recommendations: {
    part_id: string;
    part_name: string;
    allocation: Record<string, number>;
    rationale: Record<string, unknown>;
    alternative_solutions?: string[];
    primary_supplier_id?: string;
    alternate_supplier_ids?: string[];
  }[];
  sourcing_matrix?: SourcingMatrix;
  fear_greed?: FearGreedPayload;
  sim_results: SimStrategyRow[];
  scenario_insights?: ScenarioInsights;
  part_rankings: Record<string, Record<string, number>>;
  parts?: PartRow[];
  parts_by_category?: Record<string, PartRow[]>;
  suppliers?: SupplierCatalogRow[];
  company?: CompanyProfile;
  strategic?: StrategicPayload;
  parts_catalog_enriched?: PartsCatalogEnriched;
  mcdm: unknown[];
  news_headlines: NewsHeadline[];
  ai_models?: AIModelsPayload;
  digital_twin?: DigitalTwinPayload;
  command_signals?: CommandSignalsPayload;
  disruption_history?: DisruptionHistoryPayload;
  tire_disruption_brief?: TireDisruptionBrief;
};

export async function fetchDisruptionHistory(): Promise<DisruptionHistoryPayload> {
  const r = await fetch("/api/disruptions/history");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function runAnalysis(): Promise<Snapshot> {
  const r = await fetch("/api/run-analysis", { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchLatestSnapshot(): Promise<Snapshot | null> {
  const r = await fetch("/api/snapshot/latest");
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchCompanyProfile(): Promise<CompanyProfile> {
  const r = await fetch("/api/company/profile");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchStrategic(): Promise<StrategicPayload> {
  const r = await fetch("/api/company/strategic");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchScenariosCatalog(): Promise<{
  catalog: ScenarioInsights["catalog"];
  strategy_legend: Record<string, string>;
  disclaimer: string;
}> {
  const r = await fetch("/api/scenarios/catalog");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchSuppliersCatalog(): Promise<{
  total: number;
  disclaimer: string;
  trust_tiers: Record<string, { label: string; description: string }>;
  indiamart_note: string;
  suppliers: SupplierCatalogRow[];
}> {
  const r = await fetch("/api/suppliers/catalog");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchFearGreed(): Promise<FearGreedPayload> {
  const r = await fetch("/api/sentiment/fear-greed");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchSourcingMatrix(): Promise<SourcingMatrix> {
  const r = await fetch("/api/sourcing/matrix");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchAIModels(): Promise<AIModelsPayload> {
  const r = await fetch("/api/ai/models");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchDigitalTwin(): Promise<DigitalTwinPayload> {
  const r = await fetch("/api/digital-twin/status");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchCommandSignals(): Promise<CommandSignalsPayload> {
  const r = await fetch("/api/command/signals");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchPartsCatalog(): Promise<{
  total: number;
  categories: string[];
  by_category: Record<string, PartRow[]>;
}> {
  const r = await fetch("/api/parts/catalog");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchPartsCatalogEnriched(): Promise<PartsCatalogEnriched> {
  const r = await fetch("/api/parts/catalog/enriched");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchSuppliersStrategic(): Promise<SupplierStrategicPayload> {
  const r = await fetch("/api/suppliers/strategic");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

export type ChatStatus = {
  available: boolean;
  base_url: string;
  configured_model: string;
  model_ready?: boolean;
  models: string[];
  error?: string;
  hint?: string | null;
};

export async function fetchChatStatus(): Promise<ChatStatus> {
  const r = await fetch("/api/chat/status");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function streamChat(
  messages: ChatMessage[],
  onChunk: (content: string, done: boolean) => void,
  options?: { includeSnapshot?: boolean }
): Promise<void> {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages,
      stream: true,
      include_snapshot: options?.includeSnapshot ?? true,
    }),
  });
  if (!r.ok) {
    let detail = await r.text();
    try {
      const j = JSON.parse(detail) as { detail?: string };
      detail = j.detail ?? detail;
    } catch {
      /* plain text */
    }
    throw new Error(detail || `Chat failed (${r.status})`);
  }
  if (!r.body) throw new Error("No response body");

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data: ")) continue;
      try {
        const payload = JSON.parse(line.slice(6)) as {
          content?: string;
          done?: boolean;
          error?: string;
        };
        if (payload.error) throw new Error(payload.error);
        if (payload.content != null) {
          onChunk(payload.content, Boolean(payload.done));
        }
      } catch (e) {
        if (e instanceof Error && e.message !== "Unexpected end of JSON input") throw e;
      }
    }
  }
}
