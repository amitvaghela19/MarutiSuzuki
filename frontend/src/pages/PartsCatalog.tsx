import { useEffect, useMemo, useState } from "react";
import {
  fetchPartsCatalogEnriched,
  type PartsCatalogEnriched,
  type Snapshot,
} from "../api/client";
import PageHero from "../components/PageHero";
import TireDisruptionCallout from "../components/TireDisruptionCallout";

const TIRE_PART_ID = "PART-TIRE";

type Props = {
  snapshot: Snapshot | null;
  onOpenWhy: (partId: string) => void;
};

const CATEGORY_LABELS: Record<string, string> = {
  braking: "Braking",
  powertrain: "Powertrain",
  electrical: "Electrical & electronics",
  chassis: "Chassis & suspension",
  body: "Body & exterior",
  comfort: "Comfort & interior",
  safety: "Safety",
  tooling: "Tooling",
};

export default function PartsCatalog({ snapshot, onOpenWhy }: Props) {
  const [catalog, setCatalog] = useState<PartsCatalogEnriched | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const fromSnap = snapshot?.parts_catalog_enriched;
    if (fromSnap) {
      setCatalog(fromSnap);
      return;
    }
    fetchPartsCatalogEnriched()
      .then(setCatalog)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load catalog"));
  }, [snapshot]);

  const total = catalog?.total ?? 0;
  const categories = catalog?.categories ?? [];

  const filtered = useMemo(() => {
    if (!catalog) return [];
    const q = filter.trim().toLowerCase();
    let rows = catalog.parts ?? Object.values(catalog.by_category).flat();
    if (categoryFilter !== "all") {
      rows = rows.filter((p) => p.category === categoryFilter);
    }
    if (q) {
      rows = rows.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.id.toLowerCase().includes(q) ||
          (p.vehicle_system || "").toLowerCase().includes(q) ||
          p.main_commodity.toLowerCase().includes(q) ||
          p.suppliers.some((s) => s.name.toLowerCase().includes(q))
      );
    }
    return rows;
  }, [catalog, filter, categoryFilter]);

  if (err) return <div className="card glass">{err}</div>;
  if (!catalog) {
    return <div className="card glass">Loading full parts catalog…</div>;
  }

  return (
    <>
      <PageHero
        title="Parts catalog"
        subtitle={`${total} components — primary & alternate suppliers, risk, allocation why, and mitigation playbooks`}
        badge="Full BOM"
      />

      <div className="card glass parts-toolbar">
        <input
          type="search"
          className="search-input"
          placeholder="Search parts, suppliers, commodities…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          aria-label="Filter by category"
        >
          <option value="all">All categories ({total})</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {CATEGORY_LABELS[c] || c} ({(catalog.by_category[c] || []).length})
            </option>
          ))}
        </select>
        <p className="muted">
          Showing {filtered.length} of {total}. Run analysis for live risk scores and TOPSIS ranks.
        </p>
      </div>

      <div className="parts-catalog-list">
        {filtered.map((p) => {
          const open = expanded === p.id;
          return (
            <article key={p.id} className="part-detail-card glass">
              <button
                type="button"
                className="part-detail-head"
                onClick={() => setExpanded(open ? null : p.id)}
              >
                <div>
                  <strong>{p.name}</strong>
                  <code className="muted">{p.id}</code>
                </div>
                <div className="part-detail-badges">
                  <span className="badge">{CATEGORY_LABELS[p.category] || p.category}</span>
                  <span className="badge warn">Crit {p.criticality}/5</span>
                  {p.composite_risk_score != null && (
                    <span className="badge high">Risk {p.composite_risk_score}</span>
                  )}
                  <span className="badge ok">{p.supplier_count} suppliers</span>
                </div>
              </button>

              {open && (
                <div className="part-detail-body">
                  {p.id === TIRE_PART_ID && snapshot?.tire_disruption_brief && (
                    <TireDisruptionCallout brief={snapshot.tire_disruption_brief} />
                  )}
                  <p className="why-box">
                    <strong>Why / rationale:</strong> {p.why_summary}
                  </p>

                  {p.recommendation && (
                    <p className="muted">
                      Allocation:{" "}
                      {Object.entries(p.recommendation.allocation)
                        .map(([s, v]) => `${s}: ${(Number(v) * 100).toFixed(0)}%`)
                        .join(" · ")}
                    </p>
                  )}

                  <h4>Suppliers ({p.suppliers.length})</h4>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Supplier</th>
                          <th>Role</th>
                          <th>Country</th>
                          <th>Lead time</th>
                          <th>Risk</th>
                          <th>TOPSIS</th>
                        </tr>
                      </thead>
                      <tbody>
                        {p.suppliers.map((s) => (
                          <tr key={s.id}>
                            <td>
                              <strong>{s.name}</strong>
                              <br />
                              <code className="muted">{s.id}</code>
                            </td>
                            <td>
                              {s.is_primary ? (
                                <span className="badge ok">Primary</span>
                              ) : (
                                <span className="badge">Alternate</span>
                              )}
                            </td>
                            <td>{s.country_name || s.country}</td>
                            <td>{s.lead_time_days ?? "—"}d</td>
                            <td>
                              {s.risk_score != null ? (
                                <span className="badge warn">{s.risk_score}</span>
                              ) : (
                                "—"
                              )}
                            </td>
                            <td>{s.topsis_rank ?? "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {(p.alternative_solutions?.length ?? 0) > 0 && (
                    <>
                      <h4>Mitigation playbooks</h4>
                      <ul>
                        {(p.alternative_solutions ?? []).map((a) => (
                          <li key={a}>{a}</li>
                        ))}
                      </ul>
                    </>
                  )}

                  <button
                    type="button"
                    className="btn-ghost"
                    onClick={() => onOpenWhy(p.id)}
                  >
                    Open full Why panel →
                  </button>
                </div>
              )}
            </article>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="card glass">
          <p>No parts match your filters.</p>
        </div>
      )}
    </>
  );
}
