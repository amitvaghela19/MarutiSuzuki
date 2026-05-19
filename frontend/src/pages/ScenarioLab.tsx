import { useEffect, useMemo, useState } from "react";
import {
  fetchScenariosCatalog,
  type ScenarioInsights,
  type Snapshot,
} from "../api/client";

type Props = { snapshot: Snapshot | null };

const SEVERITY_CLASS: Record<string, string> = {
  low: "ok",
  medium: "warn",
  high: "high",
  critical: "high",
};

const STRATEGY_LABEL: Record<string, string> = {
  single_source: "Single source",
  dual_source: "Dual source",
  emergency_airfreight: "Emergency airfreight",
};

function MetricBar({
  label,
  value,
  max,
  variant,
}: {
  label: string;
  value: number;
  max: number;
  variant: "bad" | "good" | "neutral";
}) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="metric-bar-row">
      <span className="metric-bar-label">{label}</span>
      <div className={`metric-bar track-${variant}`}>
        <span style={{ width: `${pct}%` }} />
      </div>
      <span className="metric-bar-value">{value.toFixed(1)}</span>
    </div>
  );
}

export default function ScenarioLab({ snapshot }: Props) {
  const [catalog, setCatalog] = useState<ScenarioInsights["catalog"]>([]);
  const [legend, setLegend] = useState<Record<string, string>>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [compareMode, setCompareMode] = useState<"table" | "cards">("cards");

  const insights = snapshot?.scenario_insights;
  const hasResults = Boolean(insights?.scenarios?.length);

  useEffect(() => {
    fetchScenariosCatalog()
      .then((c) => {
        setCatalog(c.catalog);
        setLegend(c.strategy_legend);
      })
      .catch(() => {});
  }, []);

  const scenarios = insights?.scenarios ?? [];
  const categories = useMemo(() => {
    const set = new Set(scenarios.map((s) => s.category));
    catalog.forEach((c) => set.add(c.category));
    return ["all", ...Array.from(set).sort()];
  }, [scenarios, catalog]);

  const filtered = scenarios.filter(
    (s) => categoryFilter === "all" || s.category === categoryFilter
  );

  const selected =
    filtered.find((s) => s.scenario_id === selectedId) ?? filtered[0] ?? null;

  useEffect(() => {
    if (filtered.length && !selectedId) setSelectedId(filtered[0].scenario_id);
  }, [filtered, selectedId]);

  if (!snapshot) {
    return (
      <>
        <div className="card">
          <h2>Scenario Lab</h2>
          <p className="muted">
            {catalog.length} disruption scenarios configured — run <strong>analysis</strong>{" "}
            to execute Monte Carlo simulation (single vs dual vs emergency airfreight).
          </p>
        </div>
        <div className="scenario-catalog-grid">
          {catalog.map((sc) => (
            <div key={sc.id} className="card scenario-preview-card">
              <span className={`badge ${SEVERITY_CLASS[sc.severity] || "warn"}`}>
                {sc.severity}
              </span>
              <span className="badge">{sc.category}</span>
              <h3>{sc.name}</h3>
              {sc.historical_analog && (
                <p className="scenario-historical-analog">
                  <strong>Historical analog:</strong> {sc.historical_analog}
                </p>
              )}
              <p className="muted">{sc.description}</p>
              <p className="muted small">{sc.duration_days} day horizon</p>
            </div>
          ))}
        </div>
      </>
    );
  }

  if (!hasResults) {
    return <div className="card">No simulation results in snapshot. Re-run analysis.</div>;
  }

  const worst = [...filtered].sort(
    (a, b) =>
      (b.strategies.find((x) => x.strategy_id === "dual_source")?.metrics
        .stockout_probability ?? 0) -
      (a.strategies.find((x) => x.strategy_id === "dual_source")?.metrics
        .stockout_probability ?? 0)
  )[0];

  const maxStockout = Math.max(
    ...insights!.heatmap.map((h) => h.stockout_probability),
    0.01
  );

  return (
    <>
      <div className="card">
        <h2>Scenario Lab</h2>
        <p className="muted">
          {insights!.monte_carlo_runs} Monte Carlo runs per strategy ·{" "}
          {scenarios.length} scenarios · compare mitigation paths
        </p>
        {insights?.disclaimer && <p className="disclaimer">{insights.disclaimer}</p>}
        <div className="filter-row">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Category"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "All categories" : c}
              </option>
            ))}
          </select>
          <select
            value={compareMode}
            onChange={(e) => setCompareMode(e.target.value as "table" | "cards")}
            aria-label="View"
          >
            <option value="cards">Card view</option>
            <option value="table">Matrix view</option>
          </select>
        </div>
      </div>

      <div className="grid-2">
        <div className="card kpi-card">
          <h3>Highest risk scenario</h3>
          <p className="kpi-value">{worst?.name ?? "—"}</p>
          <p className="muted">{worst?.category}</p>
        </div>
        <div className="card kpi-card">
          <h3>Dual-source helps most</h3>
          <p className="kpi-value">
            {filtered.length
              ? `${(
                  Math.max(...filtered.map((s) => s.dual_source_benefit)) * 100
                ).toFixed(0)} pts`
              : "—"}
          </p>
          <p className="muted">Max stockout reduction vs single source</p>
        </div>
      </div>

      {compareMode === "table" && (
        <div className="card">
          <h3>Scenario × strategy matrix</h3>
          <p className="muted">Stockout probability (lower is better)</p>
          <div className="table-scroll">
            <table className="heatmap-table">
              <thead>
                <tr>
                  <th>Scenario</th>
                  {Object.keys(STRATEGY_LABEL).map((sid) => (
                    <th key={sid}>{STRATEGY_LABEL[sid]}</th>
                  ))}
                  <th>Recommended</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((sc) => (
                  <tr key={sc.scenario_id}>
                    <td>
                      <strong>{sc.name}</strong>
                      <br />
                      <span className={`badge ${SEVERITY_CLASS[sc.severity]}`}>
                        {sc.severity}
                      </span>
                    </td>
                    {Object.keys(STRATEGY_LABEL).map((sid) => {
                      const row = sc.strategies.find((x) => x.strategy_id === sid);
                      const p = row?.metrics.stockout_probability ?? 0;
                      const intensity = Math.min(1, p / maxStockout);
                      return (
                        <td
                          key={sid}
                          style={{
                            background: `rgba(185, 28, 28, ${0.08 + intensity * 0.35})`,
                          }}
                        >
                          {(p * 100).toFixed(1)}%
                        </td>
                      );
                    })}
                    <td>
                      <span className="badge ok">
                        {STRATEGY_LABEL[sc.recommended_strategy] || sc.recommended_strategy}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="scenario-layout">
        <div className="scenario-list">
          {filtered.map((sc) => {
            const dual = sc.strategies.find((x) => x.strategy_id === "dual_source");
            const prob = dual?.metrics.stockout_probability ?? 0;
            return (
              <button
                key={sc.scenario_id}
                type="button"
                className={`scenario-list-item ${selected?.scenario_id === sc.scenario_id ? "active" : ""}`}
                onClick={() => setSelectedId(sc.scenario_id)}
              >
                <div className="scenario-list-head">
                  <strong>{sc.name}</strong>
                  <span className={`badge ${SEVERITY_CLASS[sc.severity]}`}>{sc.severity}</span>
                </div>
                {sc.historical_analog && (
                  <p className="scenario-historical-analog small">
                    Historical: {sc.historical_analog}
                  </p>
                )}
                <p className="muted small">{sc.category}</p>
                <div className="mini-meter">
                  <span style={{ width: `${prob * 100}%` }} />
                </div>
                <span className="muted small">Dual-source stockout {(prob * 100).toFixed(0)}%</span>
              </button>
            );
          })}
        </div>

        {selected && (
          <div className="scenario-detail card">
            <h2>{selected.name}</h2>
            {selected.historical_analog && (
              <p className="scenario-historical-analog">
                <strong>Historical analog:</strong> {selected.historical_analog}
              </p>
            )}
            <p>{selected.description}</p>
            <p className="muted">
              {selected.duration_days}d horizon · shock:{" "}
              {Object.keys(selected.shock).length
                ? Object.entries(selected.shock)
                    .map(([k, v]) => `${k}=${v}`)
                    .join(", ")
                : "none"}
            </p>

            <div className="recommendation-box">
              <h3>Recommended: {STRATEGY_LABEL[selected.recommended_strategy]}</h3>
              <p>{selected.recommendation_reason}</p>
              {selected.dual_source_benefit > 0 && (
                <p className="sources-hint">
                  Dual-source benefit: −{(selected.dual_source_benefit * 100).toFixed(1)} pts
                  stockout vs single
                </p>
              )}
              {selected.scenario_id !== "BASELINE" && (
                <p className="muted">
                  vs baseline: {(selected.vs_baseline_stockout_delta * 100).toFixed(1)} pts
                  stockout delta
                </p>
              )}
            </div>

            {selected.strategies.map((st) => {
              const m = st.metrics;
              return (
                <div key={st.strategy_id} className="strategy-block">
                  <h4>
                    {STRATEGY_LABEL[st.strategy_id] || st.strategy_id}
                    {st.strategy_id === selected.recommended_strategy && (
                      <span className="badge ok"> Best</span>
                    )}
                  </h4>
                  <p className="muted small">{legend[st.strategy_id]}</p>
                  <div className="metrics-grid">
                    <div>
                      <span className="metric-label">Stockout prob.</span>
                      <strong>{(m.stockout_probability * 100).toFixed(1)}%</strong>
                    </div>
                    <div>
                      <span className="metric-label">Service level</span>
                      <strong>{m.service_level_pct?.toFixed(1)}%</strong>
                    </div>
                    <div>
                      <span className="metric-label">Avg stockouts</span>
                      <strong>{m.avg_stockouts?.toFixed(2)}</strong>
                    </div>
                    <div>
                      <span className="metric-label">P90 stockouts</span>
                      <strong>{m.p90_stockouts?.toFixed(2)}</strong>
                    </div>
                    <div>
                      <span className="metric-label">Recovery est.</span>
                      <strong>{m.recovery_days_est?.toFixed(0)} d</strong>
                    </div>
                    <div>
                      <span className="metric-label">Rel. cost</span>
                      <strong>{m.relative_cost_index?.toFixed(2)}×</strong>
                    </div>
                  </div>
                  <MetricBar
                    label="Stockout risk"
                    value={m.stockout_probability * 100}
                    max={100}
                    variant="bad"
                  />
                  <MetricBar
                    label="Service level"
                    value={m.service_level_pct ?? 0}
                    max={100}
                    variant="good"
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="card">
        <h3>Strategy legend</h3>
        <ul>
          {Object.entries(legend).map(([k, v]) => (
            <li key={k}>
              <strong>{STRATEGY_LABEL[k] || k}:</strong> {v}
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}
