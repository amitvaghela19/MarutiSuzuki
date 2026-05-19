import { useEffect, useMemo, useState } from "react";
import { fetchStrategic, type StrategicPayload } from "../api/client";
import CitedBulletList, {
  type CitedBullet,
} from "../components/CitedBulletList";

function Quadrant({
  title,
  items,
}: {
  title: string;
  items: (string | CitedBullet)[] | undefined;
}) {
  return (
    <div className="swot-quadrant">
      <h4>{title}</h4>
      <CitedBulletList items={items} />
    </div>
  );
}

function PestleColumn({
  factor,
  items,
}: {
  factor: string;
  items: (string | CitedBullet)[] | undefined;
}) {
  return (
    <div className="pestle-col">
      <h4>{factor}</h4>
      <CitedBulletList items={items} />
    </div>
  );
}

export default function StrategicAnalysis() {
  const [data, setData] = useState<StrategicPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [supplierFilter, setSupplierFilter] = useState("");
  const [openSupplier, setOpenSupplier] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategic()
      .then(setData)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  if (err) return <div className="card">{err}</div>;
  if (!data) return <div className="card">Loading SWOT & PESTLE…</div>;

  const swot = data.maruti_suzuki?.swot || {};
  const pestle = data.maruti_suzuki?.pestle || {};
  const supplierStrategic = data.supplier_strategic?.suppliers || [];
  const filteredSuppliers = useMemo(() => {
    const q = supplierFilter.trim().toLowerCase();
    if (!q) return supplierStrategic;
    return supplierStrategic.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.id.toLowerCase().includes(q) ||
        s.country.toLowerCase().includes(q)
    );
  }, [supplierStrategic, supplierFilter]);

  return (
    <>
      <div className="card">
        <h2>Maruti Suzuki India — SWOT</h2>
        <p className="muted">
          Educational synthesis from public references. Click any bullet to open its
          source website. Not from MSIL internal strategy documents.
        </p>
        {data.sources_note && <p className="sources-hint">{data.sources_note}</p>}
        <div className="swot-grid">
          <Quadrant title="Strengths" items={swot.strengths} />
          <Quadrant title="Weaknesses" items={swot.weaknesses} />
          <Quadrant title="Opportunities" items={swot.opportunities} />
          <Quadrant title="Threats" items={swot.threats} />
        </div>
      </div>

      <div className="card">
        <h2>Maruti Suzuki India — PESTLE</h2>
        <div className="pestle-grid">
          {Object.entries(pestle).map(([factor, items]) => (
            <PestleColumn key={factor} factor={factor} items={items} />
          ))}
        </div>
      </div>

      <h2 className="section-title">Partners & supply corridors</h2>
      {data.partners.map((p) => (
        <div key={p.id} className="card">
          <h3>{p.name}</h3>
          <p className="muted">{p.relationship}</p>
          <div className="grid-2">
            <div>
              <h4>Partner SWOT (summary)</h4>
              {Object.entries(p.swot_summary || {}).map(([k, items]) => (
                <div key={k}>
                  <strong>{k}</strong>
                  <CitedBulletList items={items} />
                </div>
              ))}
            </div>
            <div>
              <h4>Partner PESTLE highlights</h4>
              {Object.entries(p.pestle_highlights || {}).map(([k, items]) => (
                <div key={k}>
                  <strong>{k}</strong>
                  <CitedBulletList items={items} />
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}

      {supplierStrategic.length > 0 && (
        <>
          <h2 className="section-title">
            All suppliers — SWOT & PESTLE ({supplierStrategic.length})
          </h2>
          <div className="card glass">
            <input
              type="search"
              className="search-input"
              placeholder="Filter suppliers…"
              value={supplierFilter}
              onChange={(e) => setSupplierFilter(e.target.value)}
            />
            <p className="muted">
              Showing {filteredSuppliers.length} suppliers. See Fear & Greed tab for
              sentiment indices.
            </p>
          </div>
          {filteredSuppliers.map((s) => {
            const open = openSupplier === s.id;
            return (
              <div key={s.id} className="card glass">
                <button
                  type="button"
                  className="part-detail-head"
                  onClick={() => setOpenSupplier(open ? null : s.id)}
                >
                  <div>
                    <strong>{s.name}</strong>
                    <code className="muted">{s.id}</code>
                  </div>
                  <span className="badge">{s.country}</span>
                </button>
                {open && (
                  <div className="part-detail-body">
                    <div className="grid-2">
                      <div>
                        <h4>SWOT</h4>
                        {Object.entries(s.swot).map(([k, items]) => (
                          <div key={k}>
                            <strong>{k}</strong>
                            <CitedBulletList items={items} />
                          </div>
                        ))}
                      </div>
                      <div>
                        <h4>PESTLE</h4>
                        {Object.entries(s.pestle).map(([k, items]) => (
                          <div key={k}>
                            <strong>{k}</strong>
                            <CitedBulletList items={items} />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          {data.supplier_strategic?.disclaimer && (
            <p className="disclaimer">{data.supplier_strategic.disclaimer}</p>
          )}
        </>
      )}
    </>
  );
}
