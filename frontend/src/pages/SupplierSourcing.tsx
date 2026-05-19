import { useEffect, useMemo, useState } from "react";
import {
  fetchSourcingMatrix,
  type SourcingMatrix,
  type SourcingPartRow,
  type Snapshot,
} from "../api/client";
import { countryName } from "../utils/countries";

type Props = {
  snapshot: Snapshot | null;
  onOpenWhy: (partId: string) => void;
};

export default function SupplierSourcing({ snapshot, onOpenWhy }: Props) {
  const [matrix, setMatrix] = useState<SourcingMatrix | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [category, setCategory] = useState("all");

  useEffect(() => {
    fetchSourcingMatrix()
      .then(setMatrix)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  const data = snapshot?.sourcing_matrix ?? matrix;
  const categories = useMemo(() => {
    const set = new Set((data?.parts || []).map((p) => p.category));
    return ["all", ...Array.from(set).sort()];
  }, [data]);

  const q = filter.trim().toLowerCase();
  const rows = (data?.parts || []).filter((p) => {
    if (category !== "all" && p.category !== category) return false;
    if (!q) return true;
    const hay = [
      p.part_name,
      p.part_id,
      p.primary_supplier?.name,
      ...p.alternate_suppliers.map((s) => s.name),
      ...p.alternative_solutions,
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });

  if (err) return <div className="card">{err}</div>;
  if (!data) return <div className="card">Loading supplier sourcing matrix…</div>;

  return (
    <>
      <div className="card">
        <h2>Main suppliers & alternative solutions</h2>
        <p className="muted">
          For each part: incumbent primary supplier, approved alternates, and playbook
          mitigations. After <strong>Run analysis</strong>, recommended split allocations
          appear when risk or simulation warrants it (variable %, often 100% single source).
        </p>
        {data.disclaimer && <p className="disclaimer">{data.disclaimer}</p>}
        <div className="filter-row">
          <input
            type="search"
            className="search-input"
            placeholder="Search part, supplier, or mitigation…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="Category filter"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "All categories" : c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {rows.map((p) => (
        <SourcingCard key={p.part_id} row={p} onOpenWhy={onOpenWhy} />
      ))}

      {rows.length === 0 && (
        <div className="card">
          <p>No rows match your filters.</p>
        </div>
      )}

      {data.suppliers_index && data.suppliers_index.length > 0 && (
        <div className="card">
          <h2>Supplier coverage index</h2>
          <p className="muted">Which parts each archetype supplies as primary vs alternate.</p>
          <div className="supplier-index-grid">
            {data.suppliers_index.map((entry) => (
              <div key={entry.supplier.id} className="supplier-index-card">
                <h4>{entry.supplier.name}</h4>
                <p className="muted">
                  {countryName(entry.supplier.country, entry.supplier.country_name)} ·{" "}
                  {entry.supplier.lead_time_days}d lead · risk{" "}
                  {entry.supplier.risk_score?.toFixed(1) ?? "—"}
                </p>
                <p>
                  <strong>Primary for:</strong>{" "}
                  {entry.primary_for_parts.length
                    ? entry.primary_for_parts.map((x) => x.part_name).join("; ")
                    : "—"}
                </p>
                <p>
                  <strong>Alternate for:</strong>{" "}
                  {entry.alternate_for_parts.length
                    ? entry.alternate_for_parts.map((x) => x.part_name).join("; ")
                    : "—"}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function SourcingCard({
  row,
  onOpenWhy,
}: {
  row: SourcingPartRow;
  onOpenWhy: (id: string) => void;
}) {
  const primary = row.primary_supplier;
  const alloc = row.recommended_allocation;
  const mode = row.allocation_mode;
  const isSingle =
    mode === "single_source" ||
    (alloc && Object.keys(alloc).length === 1) ||
    (alloc &&
      Object.values(alloc).length === 1 &&
      Object.values(alloc)[0] >= 0.99);

  const formatAlloc = () => {
    if (!alloc) return null;
    const nameFor = (id: string) => {
      if (primary?.id === id) return primary.name;
      const alt = row.alternate_suppliers.find((s) => s.id === id);
      return alt?.name ?? id;
    };
    return Object.entries(alloc)
      .sort((a, b) => b[1] - a[1])
      .map(([id, pct]) => `${nameFor(id)}: ${(pct * 100).toFixed(0)}%`)
      .join(" · ");
  };

  return (
    <div className="card sourcing-card">
      <div className="sourcing-card-header">
        <div>
          <h3>{row.part_name}</h3>
          <p className="muted">
            {row.category} · {row.main_commodity} · criticality {row.criticality}/5
          </p>
        </div>
        <button type="button" onClick={() => onOpenWhy(row.part_id)}>
          Why / allocation
        </button>
      </div>

      <div className="grid-2">
        <div>
          <h4 className="label-primary">Main supplier</h4>
          {primary ? (
            <ul className="supplier-block">
              <li>
                <strong>{primary.name}</strong> (
                {countryName(primary.country, primary.country_name)})
              </li>
              <li>Lead time: {primary.lead_time_days} days</li>
              {primary.risk_score !== undefined && (
                <li>
                  Risk score: <span className="badge warn">{primary.risk_score}</span>
                </li>
              )}
            </ul>
          ) : (
            <p>Not configured</p>
          )}
        </div>
        <div>
          <h4>Approved alternates</h4>
          {row.alternate_suppliers.length === 0 ? (
            <p className="muted">None listed</p>
          ) : (
            <ul className="supplier-block">
              {row.alternate_suppliers.map((s) => (
                <li key={s.id}>
                  <strong>{s.name}</strong> ({countryName(s.country, s.country_name)}) —{" "}
                  {s.lead_time_days}d
                  {s.risk_score !== undefined && (
                    <>
                      {" "}
                      · risk <span className="badge warn">{s.risk_score}</span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {alloc && Object.keys(alloc).length > 0 && (
        <p className="allocation-line">
          <strong>{isSingle ? "Sourcing:" : "Recommended split:"}</strong>{" "}
          {formatAlloc()}
          {mode && mode !== "single_source" && (
            <span className="badge ok" style={{ marginLeft: "0.5rem" }}>
              {mode.replace(/_/g, " ")}
            </span>
          )}
        </p>
      )}
      {!alloc && (
        <p className="muted">
          Run analysis to compute risk-based allocation (single source or variable split — not a
          fixed 60/40).
        </p>
      )}

      <h4>Alternative solutions (mitigations)</h4>
      <ul>
        {row.alternative_solutions.map((sol) => (
          <li key={sol}>{sol}</li>
        ))}
      </ul>
    </div>
  );
}
