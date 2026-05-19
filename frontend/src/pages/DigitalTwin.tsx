import { useEffect, useState } from "react";
import {
  fetchDigitalTwin,
  type DigitalTwinPayload,
  type Snapshot,
} from "../api/client";
import PageHero from "../components/PageHero";
import KpiStrip from "../components/KpiStrip";

type Props = { snapshot: Snapshot | null; embedded?: boolean };

export default function DigitalTwin({ snapshot, embedded }: Props) {
  const [data, setData] = useState<DigitalTwinPayload | null>(null);

  useEffect(() => {
    if (snapshot?.digital_twin) {
      setData(snapshot.digital_twin);
      return;
    }
    fetchDigitalTwin().then(setData).catch(() => setData(null));
  }, [snapshot]);

  const twin = snapshot?.digital_twin ?? data;
  if (!twin) {
    return (
      <div className="card glass">
        <p>Loading digital twin…</p>
      </div>
    );
  }

  const g = twin.global_kpis;
  return (
    <>
      {!embedded && (
        <PageHero
          title="Plant Digital Twin"
          subtitle="Real-time synthetic telemetry across Gurgaon, Manesar, and Gujarat"
          badge="Twin mesh"
        />
      )}
      <KpiStrip
        items={[
          { label: "Plants", value: g.total_plants, tone: "accent" },
          { label: "Avg OEE", value: `${g.avg_oee_pct}%`, tone: "ok" },
          {
            label: "Network",
            value: twin.network_health,
            tone: twin.network_health === "green" ? "ok" : "warn",
          },
          {
            label: "Constrained",
            value: g.plants_constrained,
            tone: g.plants_constrained ? "warn" : "ok",
          },
        ]}
      />
      <div className="twin-plant-grid">
        {twin.plants.map((plant) => (
          <article key={plant.id} className="card glass twin-plant-card">
            <div className="twin-plant-head">
              <h2>{plant.name}</h2>
              <span
                className={`badge ${
                  plant.metrics.status === "nominal" ? "ok" : "warn"
                }`}
              >
                {plant.metrics.status}
              </span>
            </div>
            <p className="muted">{plant.location}</p>
            <div className="twin-metrics-grid">
              <div>
                <span className="metric-label">Throughput / hr</span>
                <strong>{plant.metrics.throughput_units_per_hour}</strong>
              </div>
              <div>
                <span className="metric-label">Buffer (days)</span>
                <strong>{plant.metrics.buffer_days_of_supply}</strong>
              </div>
              <div>
                <span className="metric-label">OEE</span>
                <strong>{plant.metrics.oee_pct}%</strong>
              </div>
              <div>
                <span className="metric-label">Quality PPM</span>
                <strong>{plant.metrics.quality_ppm}</strong>
              </div>
            </div>
            <div className="risk-bar twin-oee-bar">
              <span style={{ width: `${plant.metrics.oee_pct}%` }} />
            </div>
            {plant.bottlenecks.length > 0 && (
              <>
                <h3 className="section-mini">Bottleneck parts</h3>
                <ul className="bottleneck-list">
                  {plant.bottlenecks.map((b) => (
                    <li key={b.part_id}>
                      {b.part_name}{" "}
                      <span className="badge high">risk {b.risk_score}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}
            <h3 className="section-mini">Lines</h3>
            <ul className="chip-list">
              {plant.lines.map((l) => (
                <li key={l.id}>
                  {l.name}: {l.utilization_pct}%
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
      {twin.disclaimer && <p className="disclaimer">{twin.disclaimer}</p>}
    </>
  );
}
