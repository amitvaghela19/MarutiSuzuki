import { useEffect, useState } from "react";
import {
  fetchAIModels,
  type AIModelsPayload,
  type Snapshot,
} from "../api/client";
import ModelCard from "../components/ModelCard";
import PageHero from "../components/PageHero";
import KpiStrip from "../components/KpiStrip";

type Props = { snapshot: Snapshot | null; embedded?: boolean };

export default function AIHub({ snapshot, embedded }: Props) {
  const [data, setData] = useState<AIModelsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    const fromSnap = snapshot?.ai_models;
    if (fromSnap) {
      setData(fromSnap);
      return;
    }
    fetchAIModels()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [snapshot]);

  const payload = snapshot?.ai_models ?? data;
  if (error && !payload) {
    return <div className="card glass">{error}</div>;
  }
  if (!payload) {
    return (
      <div className="card glass">
        <p>Loading AI model registry…</p>
      </div>
    );
  }

  const s = payload.summary;
  return (
    <>
      {!embedded && (
        <PageHero
          title="AI & Model Fleet"
          subtitle="Graph neural risk, transformers, RL allocation, digital twin, and MCDM engines"
          badge="Neural ops"
        />
      )}
      <KpiStrip
        items={[
          { label: "Models", value: s.total_models, tone: "accent" },
          { label: "Active", value: s.active, tone: "ok" },
          { label: "Training", value: s.training, tone: "warn" },
          {
            label: "Fleet confidence",
            value: `${(s.avg_confidence * 100).toFixed(0)}%`,
            tone: "accent",
          },
          {
            label: "Fleet health",
            value: s.fleet_health,
            tone: s.fleet_health === "optimal" ? "ok" : "warn",
          },
        ]}
      />
      <section className="card glass">
        <h2>ML pipelines</h2>
        <div className="pipeline-grid">
          {payload.pipelines.map((p) => (
            <div key={p.id} className="pipeline-card">
              <div className="pipeline-head">
                <strong>{p.name}</strong>
                <span className={`badge ${p.status === "live" ? "ok" : "stale"}`}>
                  {p.status}
                </span>
              </div>
              <ul>
                {p.stages.map((st) => (
                  <li key={st}>{st}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
      <section className="model-grid">
        {payload.models.map((m) => (
          <ModelCard
            key={m.id}
            model={m}
            expanded={expandedId === m.id}
            onToggle={() => setExpandedId((id) => (id === m.id ? null : m.id))}
          />
        ))}
      </section>
      <p className="muted model-grid-hint">Click any model card to open a plain-language brief.</p>
      {payload.disclaimer && <p className="disclaimer">{payload.disclaimer}</p>}
    </>
  );
}
