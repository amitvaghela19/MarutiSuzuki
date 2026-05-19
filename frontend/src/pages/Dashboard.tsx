import { useEffect, useMemo, useRef, useState } from "react";
import type { CommandSignal, NewsHeadline, Snapshot } from "../api/client";
import PageHero from "../components/PageHero";
import KpiStrip from "../components/KpiStrip";
import SignalDetailDrawer from "../components/SignalDetailDrawer";
import DisruptionTimeline from "../components/DisruptionTimeline";
import TireDisruptionCallout from "../components/TireDisruptionCallout";
import { countryName } from "../utils/countries";

type Props = {
  snapshot: Snapshot | null;
  onOpenWhy: (partId: string) => void;
  onNavigate?: (tab: string, entityId?: string | null) => void;
  focusSeverity?: string | null;
  focusSignalId?: string | null;
};

const severityClass: Record<string, string> = {
  critical: "high",
  high: "high",
  medium: "warn",
  low: "ok",
};

function newsSeverityBadge(sev?: number): { label: string; className: string } {
  if (!sev || sev < 2) return { label: "low", className: "ok" };
  if (sev >= 5) return { label: "critical", className: "high" };
  if (sev >= 4) return { label: "high", className: "high" };
  return { label: "medium", className: "warn" };
}

function signalForNews(
  signals: CommandSignal[],
  index: number,
  title: string
): CommandSignal | undefined {
  return signals.find(
    (s) =>
      s.category === "news" &&
      (s.news_index === index || s.title === title.slice(0, 120))
  );
}

function RiskList({
  title,
  items,
}: {
  title: string;
  items: { label: string; score: number }[];
}) {
  return (
    <div className="card glass">
      <h2>{title}</h2>
      <ul className="risk-list">
        {items.map((x) => (
          <li key={x.label}>
            <div className="risk-row">
              <span>{x.label}</span>
              <strong>{x.score.toFixed(1)}</strong>
            </div>
            <div className="risk-bar">
              <span style={{ width: `${Math.min(100, x.score)}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function Dashboard({
  snapshot,
  onOpenWhy,
  onNavigate,
  focusSeverity,
  focusSignalId,
}: Props) {
  const [severityFilter, setSeverityFilter] = useState<string | "all">("all");
  const [selectedSignal, setSelectedSignal] = useState<CommandSignal | null>(null);
  const [selectedNews, setSelectedNews] = useState<NewsHeadline | null>(null);
  const signalsRef = useRef<HTMLElement | null>(null);

  const signals = snapshot?.command_signals;

  useEffect(() => {
    if (focusSeverity) setSeverityFilter(focusSeverity);
  }, [focusSeverity]);

  useEffect(() => {
    if (!focusSignalId || !signals?.signals.length) return;
    const match = signals.signals.find((s) => s.id === focusSignalId);
    if (match) {
      setSelectedSignal(match);
      setSelectedNews(null);
      setSeverityFilter(match.severity);
      signalsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [focusSignalId, signals]);

  const filteredSignals = useMemo(() => {
    const list = signals?.signals ?? [];
    if (severityFilter === "all") return list;
    return list.filter((s) => s.severity === severityFilter);
  }, [signals, severityFilter]);

  const openNews = (n: NewsHeadline, index: number) => {
    const linked = signalForNews(signals?.signals ?? [], index, n.title);
    if (linked) {
      setSelectedSignal(linked);
      setSelectedNews(n);
    } else {
      setSelectedSignal(null);
      setSelectedNews(n);
    }
  };

  if (!snapshot) {
    return (
      <>
        <PageHero
          title="Command Center"
          subtitle="Run the full ingest → risk → MCDM → simulation pipeline"
          badge="Awaiting run"
        />
        <div className="card glass empty-state">
          <p>
            No analysis yet. Click <strong>Run analysis</strong> to activate AI
            models, digital twin telemetry, and ops signals.
          </p>
        </div>
      </>
    );
  }

  const health = Object.entries(snapshot.data_health || {});
  const partsCount =
    snapshot.parts?.length ??
    Object.values(snapshot.parts_by_category || {}).flat().length;
  const categories = Object.keys(snapshot.parts_by_category || {});
  const sig = snapshot.command_signals;
  const scenarios = snapshot.scenario_insights?.scenarios?.length ?? 0;

  return (
    <>
      <PageHero
        title="Command Center"
        subtitle="Ops signals, news, risks, and recommendations in one view"
        badge="Live"
      />
      {snapshot.tire_disruption_brief && (
        <TireDisruptionCallout
          brief={snapshot.tire_disruption_brief}
          onNavigateParts={() => onNavigate?.("parts", snapshot.tire_disruption_brief?.navigate_part_id)}
          onNavigateScenario={() => onNavigate?.("scenarios")}
        />
      )}

      {snapshot.disruption_history && (
        <div className="card glass disruption-teaser">
          <h2 className="section-title">Past disruptions</h2>
          <p className="muted">
            Educational context from public sources — open Enterprise → Disruption history
            for the full timeline.
          </p>
          <DisruptionTimeline
            history={snapshot.disruption_history}
            compact
            maxItems={2}
          />
          <button
            type="button"
            className="btn-ghost"
            onClick={() => onNavigate?.("enterprise")}
          >
            Full disruption history →
          </button>
        </div>
      )}

      <KpiStrip
        items={[
          { label: "Parts", value: partsCount, tone: "accent" },
          {
            label: "Signals",
            value: sig?.total ?? 0,
            hint: sig?.critical_count ? `${sig.critical_count} critical` : undefined,
            tone: sig?.critical_count ? "bad" : "accent",
            onClick: () => {
              setSeverityFilter(sig?.critical_count ? "critical" : "all");
              signalsRef.current?.scrollIntoView({ behavior: "smooth" });
            },
          },
          {
            label: "Critical",
            value: sig?.critical_count ?? 0,
            tone: (sig?.critical_count ?? 0) > 0 ? "bad" : "ok",
            onClick: () => {
              setSeverityFilter("critical");
              signalsRef.current?.scrollIntoView({ behavior: "smooth" });
            },
          },
          { label: "Scenarios", value: scenarios, tone: "accent" },
        ]}
      />

      <section ref={signalsRef} className="signal-section">
        <div className="signal-section-head">
          <h2 className="section-title">Ops pulse — prioritized signals</h2>
          <div className="severity-filters" role="tablist">
            {(["all", "critical", "high", "medium"] as const).map((sev) => (
              <button
                key={sev}
                type="button"
                role="tab"
                className={severityFilter === sev ? "active" : ""}
                onClick={() => setSeverityFilter(sev)}
              >
                {sev === "all" ? "All" : sev}
                {sev === "critical" && sig ? ` (${sig.critical_count})` : ""}
                {sev === "high" && sig ? ` (${sig.high_count})` : ""}
              </button>
            ))}
          </div>
        </div>
        <div className="signal-feed">
          {filteredSignals.length === 0 ? (
            <div className="card glass">
              <p className="muted">No signals at this severity. Try another filter.</p>
            </div>
          ) : (
            filteredSignals.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`signal-card glass severity-${s.severity} signal-card-clickable${
                  selectedSignal?.id === s.id ? " signal-card-selected" : ""
                }`}
                onClick={() => {
                  setSelectedSignal(s);
                  if (s.category === "news" && s.news_index != null) {
                    setSelectedNews(snapshot.news_headlines[s.news_index] ?? null);
                  } else {
                    setSelectedNews(null);
                  }
                }}
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
                <span className="signal-action-hint">Click for why →</span>
              </button>
            ))
          )}
        </div>
        {sig?.last_refresh_note && (
          <p className="muted signal-footnote">{sig.last_refresh_note}</p>
        )}
      </section>

      {snapshot.news_headlines?.length > 0 && (
        <div className="card glass">
          <h2>News sentinel</h2>
          <p className="muted">
            Click a headline to see why it was flagged and how it links to ops signals.
          </p>
          <ul className="headline-list headline-list-clickable">
            {snapshot.news_headlines.map((n, i) => {
              const badge = newsSeverityBadge(n.severity);
              const linked = signalForNews(sig?.signals ?? [], i, n.title);
              return (
                <li key={`${i}-${n.title.slice(0, 24)}`}>
                  <button
                    type="button"
                    className="headline-row"
                    onClick={() => openNews(n, i)}
                  >
                    <span className="headline-title">{n.title}</span>
                    <span className={`badge ${badge.className}`}>{badge.label}</span>
                    {n.risk_type && (
                      <span className="badge warn">{n.risk_type}</span>
                    )}
                    {linked && (
                      <span className="badge high">In signals</span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      <div className="grid-2">
        <div className="card glass">
          <h2>Pipeline health</h2>
          <p className="muted">
            <code>{snapshot.run_id.slice(0, 8)}</code> ·{" "}
            {new Date(snapshot.generated_at).toLocaleString()}
          </p>
          <div className="chip-list health-chips">
            {health.map(([k, v]) => (
              <li key={k}>
                <span className={`badge ${v === "ok" ? "ok" : "stale"}`}>
                  {k}: {v}
                </span>
              </li>
            ))}
          </div>
        </div>
        <div className="card glass">
          <h2>Parts under watch</h2>
          <p>
            <strong>{partsCount}</strong> components across{" "}
            <strong>{categories.length || "—"}</strong> categories.
          </p>
          {categories.length > 0 && (
            <ul className="chip-list">
              {categories.map((c) => (
                <li key={c}>
                  {c} ({(snapshot.parts_by_category?.[c] || []).length})
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="grid-2">
        <RiskList
          title="Top country risks"
          items={[...snapshot.country_risks]
            .sort((a, b) => b.score - a.score)
            .slice(0, 5)
            .map((r) => ({ label: countryName(r.code, r.name), score: r.score }))}
        />
        <RiskList
          title="Top supplier risks"
          items={[...snapshot.supplier_risks]
            .sort((a, b) => b.score - a.score)
            .slice(0, 5)
            .map((r) => ({ label: r.id, score: r.score }))}
        />
      </div>

      <div className="card glass">
        <h2>Headline recommendations</h2>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Part</th>
                <th>Allocation</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {snapshot.recommendations.map((rec) => (
                <tr key={rec.part_id}>
                  <td>{rec.part_name}</td>
                  <td>
                    {Object.entries(rec.allocation)
                      .map(([s, p]) => `${s}: ${(p * 100).toFixed(0)}%`)
                      .join(", ")}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn-ghost"
                      onClick={() => onOpenWhy(rec.part_id)}
                    >
                      Why?
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {(selectedSignal || selectedNews) && (
        <SignalDetailDrawer
          signal={selectedSignal}
          news={selectedNews}
          onClose={() => {
            setSelectedSignal(null);
            setSelectedNews(null);
          }}
          onNavigate={onNavigate}
        />
      )}
    </>
  );
}
