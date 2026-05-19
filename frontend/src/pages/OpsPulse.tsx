import { useEffect, useState } from "react";
import {
  fetchCommandSignals,
  type CommandSignalsPayload,
  type Snapshot,
} from "../api/client";
import PageHero from "../components/PageHero";
import KpiStrip from "../components/KpiStrip";

type Props = {
  snapshot: Snapshot | null;
  onNavigate?: (tab: string) => void;
};

const severityClass: Record<string, string> = {
  critical: "high",
  high: "high",
  medium: "warn",
  low: "ok",
};

export default function OpsPulse({ snapshot }: Props) {
  const [data, setData] = useState<CommandSignalsPayload | null>(null);

  useEffect(() => {
    if (snapshot?.command_signals) {
      setData(snapshot.command_signals);
      return;
    }
    fetchCommandSignals().then(setData).catch(() => setData(null));
  }, [snapshot]);

  const signals = snapshot?.command_signals ?? data;
  if (!signals) {
    return (
      <div className="card glass">
        <p>Loading operational signals…</p>
      </div>
    );
  }

  return (
    <>
      <PageHero
        title="Ops Pulse"
        subtitle="Prioritized alerts from risk, news, scenarios, and sourcing — advisory autopilot"
        badge="Signal stream"
      />
      <KpiStrip
        items={[
          { label: "Signals", value: signals.total, tone: "accent" },
          { label: "Critical", value: signals.critical_count, tone: "bad" },
          { label: "High", value: signals.high_count, tone: "warn" },
          {
            label: "Autopilot",
            value: signals.autopilot_mode,
            tone: "accent",
          },
        ]}
      />
      <div className="signal-feed">
        {signals.signals.length === 0 ? (
          <div className="card glass">
            <p className="muted">
              No elevated signals in baseline mode. Run analysis for live prioritization.
            </p>
          </div>
        ) : (
          signals.signals.map((s) => (
            <article
              key={s.id}
              className={`signal-card glass severity-${s.severity}`}
            >
              <div className="signal-card-head">
                <span className={`badge ${severityClass[s.severity] || "warn"}`}>
                  {s.severity}
                </span>
                <span className="signal-category">{s.category}</span>
                <span className="signal-priority">P{s.priority}</span>
              </div>
              <h3>{s.title}</h3>
              <p className="muted">{s.detail}</p>
              <p className="signal-action">→ {s.action}</p>
            </article>
          ))
        )}
      </div>
      <p className="muted">{signals.last_refresh_note}</p>
    </>
  );
}
