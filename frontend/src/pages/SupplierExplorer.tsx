import { useEffect, useMemo, useState } from "react";
import {
  fetchSourcingMatrix,
  fetchSuppliersCatalog,
  fetchSuppliersStrategic,
  type Snapshot,
  type SupplierCatalogRow,
  type SupplierStrategicProfile,
} from "../api/client";
import FearGreedGauge from "../components/FearGreedGauge";
import CitedBulletList from "../components/CitedBulletList";
import SupplierNameLink from "../components/SupplierNameLink";
import { countryName } from "../utils/countries";

type Props = {
  snapshot: Snapshot | null;
  onOpenWhy: (partId: string) => void;
};

const TRUST_LABELS: Record<string, string> = {
  oem_tier1: "OEM Tier-1",
  acma_cluster: "ACMA cluster",
  indiamart_verified: "IndiaMART verified",
};

export default function SupplierExplorer({ snapshot, onOpenWhy }: Props) {
  const [filter, setFilter] = useState("");
  const [trustFilter, setTrustFilter] = useState("all");
  const [selected, setSelected] = useState<string | null>(null);
  const [catalog, setCatalog] = useState<SupplierCatalogRow[]>([]);
  const [indiamartNote, setIndiamartNote] = useState("");
  const [strategicMap, setStrategicMap] = useState<
    Record<string, SupplierStrategicProfile>
  >({});
  const [index, setIndex] = useState<
    | {
        supplier: { id: string; name: string; country: string; lead_time_days?: number };
        primary_for_parts: { part_id: string; part_name: string }[];
        alternate_for_parts: { part_id: string; part_name: string }[];
      }[]
    | null
  >(null);

  useEffect(() => {
    fetchSuppliersCatalog()
      .then((c) => {
        setCatalog(c.suppliers);
        setIndiamartNote(c.indiamart_note || "");
      })
      .catch(() => {});
    fetchSuppliersStrategic()
      .then((s) => {
        const map: Record<string, SupplierStrategicProfile> = {};
        s.suppliers.forEach((sup) => {
          map[sup.id] = sup;
        });
        setStrategicMap(map);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (snapshot?.sourcing_matrix?.suppliers_index) {
      setIndex(snapshot.sourcing_matrix.suppliers_index);
      return;
    }
    fetchSourcingMatrix()
      .then((m) => setIndex(m.suppliers_index))
      .catch(() => setIndex(null));
  }, [snapshot]);

  const rows = useMemo(() => {
    const supMap = snapshot
      ? Object.fromEntries(snapshot.supplier_risks.map((s) => [s.id, s.score]))
      : {};
    const fgMap = Object.fromEntries(
      (snapshot?.fear_greed?.suppliers || []).map((s) => [s.id, s])
    );
    const base = catalog.length
      ? catalog
      : (snapshot?.suppliers || []).map((s) => ({ ...s } as SupplierCatalogRow));

    return base.map((s) => {
      const fg = fgMap[s.id];
      return {
        id: s.id,
        name: s.name,
        country: s.country,
        countryLabel: countryName(s.country, s.country_name),
        city: s.city,
        trustTier: s.trust_tier || "oem_tier1",
        trustLabel: TRUST_LABELS[s.trust_tier || ""] || s.trust_tier,
        indiamartCategory: s.indiamart_category,
        referenceUrl: s.reference_url,
        commodities: s.commodities?.join(", ") || "",
        leadTime: s.lead_time_days,
        risk: supMap[s.id],
        fear: fg?.fear_index,
        greed: fg?.greed_index,
      };
    });
  }, [snapshot, catalog]);

  const filtered = rows.filter((r) => {
    if (trustFilter !== "all" && r.trustTier !== trustFilter) return false;
    if (!filter.trim()) return true;
    const q = filter.toLowerCase();
    return (
      r.name.toLowerCase().includes(q) ||
      r.id.toLowerCase().includes(q) ||
      r.countryLabel.toLowerCase().includes(q) ||
      (r.city || "").toLowerCase().includes(q) ||
      (r.indiamartCategory || "").toLowerCase().includes(q) ||
      r.commodities.toLowerCase().includes(q)
    );
  });

  const selectedEntry = index?.find((e) => e.supplier.id === selected);
  const selectedFg = (snapshot?.fear_greed?.suppliers || []).find(
    (s) => s.id === selected
  );
  const selectedStrategic = selected ? strategicMap[selected] : undefined;
  const hasScores = Boolean(snapshot);

  return (
    <>
      <div className="card">
        <h2>Supplier Explorer</h2>
        <p className="muted">
          <strong>{rows.length}</strong> suppliers — OEM Tier-1, Indian ACMA-style clusters, and
          IndiaMART category-mapped discovery (trusted public category links only).
        </p>
        {indiamartNote && <p className="disclaimer">{indiamartNote}</p>}
        {!hasScores && (
          <p className="sources-hint">
            Run <strong>analysis</strong> to populate risk, fear, and greed scores.
          </p>
        )}
        <div className="filter-row">
          <input
            placeholder="Search name, city, commodity, IndiaMART category…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
          <select
            value={trustFilter}
            onChange={(e) => setTrustFilter(e.target.value)}
            aria-label="Trust tier filter"
          >
            <option value="all">All trust tiers</option>
            <option value="oem_tier1">OEM Tier-1</option>
            <option value="acma_cluster">ACMA cluster</option>
            <option value="indiamart_verified">IndiaMART verified</option>
          </select>
        </div>
        <p className="muted" style={{ marginTop: "0.5rem" }}>
          Showing {filtered.length} of {rows.length}
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Location</th>
                <th>Trust</th>
                <th>IndiaMART</th>
                <th>Commodities</th>
                <th>Lead (d)</th>
                {hasScores && (
                  <>
                    <th>Risk</th>
                    <th>Fear</th>
                    <th>Greed</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr
                  key={r.id}
                  onClick={() => setSelected(r.id)}
                  className={selected === r.id ? "row-selected" : undefined}
                >
                  <td>
                    <SupplierNameLink name={r.name} referenceUrl={r.referenceUrl} />
                    <br />
                    <code className="muted">{r.id}</code>
                  </td>
                  <td>
                    {r.city ? `${r.city}, ` : ""}
                    {r.countryLabel}
                  </td>
                  <td>
                    <span className={`badge trust-${r.trustTier}`}>{r.trustLabel}</span>
                  </td>
                  <td>
                    {r.referenceUrl ? (
                      <a
                        href={r.referenceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bullet-link"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {r.indiamartCategory || "Category"} ↗
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="muted small">{r.commodities}</td>
                  <td>{r.leadTime ?? "—"}</td>
                  {hasScores && (
                    <>
                      <td>
                        {r.risk !== undefined ? (
                          <span className={r.risk >= 70 ? "badge high" : "badge warn"}>
                            {r.risk.toFixed(1)}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {r.fear !== undefined ? (
                          <span className="fg-inline meter-fear-inline">{r.fear.toFixed(0)}</span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {r.greed !== undefined ? (
                          <span className="fg-inline meter-greed-inline">{r.greed.toFixed(0)}</span>
                        ) : (
                          "—"
                        )}
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedEntry && (
        <div className="card glass supplier-detail-panel">
          <h3>{selectedEntry.supplier.name}</h3>
          <p className="muted">{selectedEntry.supplier.id}</p>

          {selectedFg && (
            <FearGreedGauge
              name={selectedFg.name}
              subtitle={countryName(selectedFg.country, selectedFg.country_name)}
              fear={selectedFg.fear_index}
              greed={selectedFg.greed_index}
              label={selectedFg.sentiment_label}
              drivers={selectedFg.drivers}
            />
          )}

          {selectedStrategic && (
            <div className="supplier-strategic-block">
              <h4>SWOT</h4>
              <div className="swot-grid">
                {Object.entries(selectedStrategic.swot).map(([k, bullets]) => (
                  <div key={k} className="swot-quadrant">
                    <h5>{k}</h5>
                    <CitedBulletList items={bullets} />
                  </div>
                ))}
              </div>
              <h4>PESTLE</h4>
              <div className="pestle-grid">
                {Object.entries(selectedStrategic.pestle).map(([k, bullets]) => (
                  <div key={k} className="pestle-col">
                    <h5>{k}</h5>
                    <CitedBulletList items={bullets} />
                  </div>
                ))}
              </div>
            </div>
          )}

          <h4>Main supplier for</h4>
          {selectedEntry.primary_for_parts.length === 0 ? (
            <p className="muted">No primary assignments in config.</p>
          ) : (
            <ul>
              {selectedEntry.primary_for_parts.map((p) => (
                <li key={p.part_id}>
                  {p.part_name}{" "}
                  <button type="button" onClick={() => onOpenWhy(p.part_id)}>
                    Details
                  </button>
                </li>
              ))}
            </ul>
          )}
          <h4>Alternate / backup for</h4>
          {selectedEntry.alternate_for_parts.length === 0 ? (
            <p className="muted">None — candidate for IndiaMART discovery pool</p>
          ) : (
            <ul>
              {selectedEntry.alternate_for_parts.map((p) => (
                <li key={p.part_id}>
                  {p.part_name}{" "}
                  <button type="button" onClick={() => onOpenWhy(p.part_id)}>
                    Details
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </>
  );
}
