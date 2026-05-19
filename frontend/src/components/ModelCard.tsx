export type ModelReportNewsItem = {
  title: string;
  summary?: string;
  severity?: number;
  risk_type?: string;
};

export type ModelReportSection = {
  title: string;
  body: string;
  bullets?: string[];
  news_items?: ModelReportNewsItem[];
};

export type ModelReport = {
  headline: string;
  lede: string;
  sections: ModelReportSection[];
};

export type AIModel = {
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
  report?: ModelReport;
};

type Props = {
  model: AIModel;
  expanded: boolean;
  onToggle: () => void;
};

export default function ModelCard({ model, expanded, onToggle }: Props) {
  const conf = model.confidence != null ? `${(model.confidence * 100).toFixed(0)}%` : "—";
  const report = model.report;

  return (
    <article
      className={`model-card glass ${expanded ? "model-card-expanded" : ""}`}
      data-model-id={model.id}
    >
      <button
        type="button"
        className="model-card-toggle"
        onClick={onToggle}
        aria-expanded={expanded}
        aria-controls={`model-report-${model.id}`}
      >
        <div className="model-card-head">
          <h3>{model.name}</h3>
          <span className={`badge model-status-${model.status}`}>{model.status}</span>
        </div>
        <p className="muted model-family">
          {model.family} · v{model.version}
        </p>
        <p className="model-desc">{model.description}</p>
        <div className="model-metrics">
          <div>
            <span className="metric-label">Confidence</span>
            <strong>{conf}</strong>
          </div>
          <div>
            <span className="metric-label">Latency</span>
            <strong>{model.latency_ms ?? "—"}ms</strong>
          </div>
          <div>
            <span className="metric-label">Demo accuracy</span>
            <strong>
              {model.accuracy_demo != null
                ? `${(model.accuracy_demo * 100).toFixed(0)}%`
                : "—"}
            </strong>
          </div>
        </div>
        {model.live_note && <p className="model-live-note">{model.live_note}</p>}
        <div className="model-card-actions">
          {model.health === "watch" && <span className="badge warn">Drift watch</span>}
          <span className="model-expand-hint">{expanded ? "Show less ↑" : "Read full brief →"}</span>
        </div>
      </button>

      {expanded && (
        <div
          id={`model-report-${model.id}`}
          className="model-report"
          role="region"
          aria-label={`${model.name} detailed brief`}
        >
          {report ? (
            <>
              <h4 className="model-report-headline">{report.headline}</h4>
              <p className="model-report-lede">{report.lede}</p>
              {report.sections.map((sec) => (
                <section key={sec.title} className="model-report-section">
                  <h5>{sec.title}</h5>
                  {sec.body ? <p>{sec.body}</p> : null}
                  {sec.bullets && sec.bullets.length > 0 && (
                    <ul className="model-report-bullets">
                      {sec.bullets.map((b) => (
                        <li key={b.slice(0, 48)}>{b}</li>
                      ))}
                    </ul>
                  )}
                  {sec.news_items && sec.news_items.length > 0 && (
                    <ul className="model-report-news">
                      {sec.news_items.map((n) => (
                        <li key={n.title}>
                          <strong>{n.title}</strong>
                          {n.severity != null && (
                            <span className="model-report-news-meta">
                              {" "}
                              · severity {n.severity}/5 · {n.risk_type?.replace(/_/g, " ")}
                            </span>
                          )}
                          {n.summary ? <p className="model-report-news-summary">{n.summary}</p> : null}
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              ))}
              {model.last_trained && (
                <p className="model-report-footer muted">
                  Last refreshed in demo registry: {model.last_trained}
                </p>
              )}
            </>
          ) : (
            <p className="model-report-lede muted">
              Re-run <strong>Run analysis</strong> on the home page (or refresh from the API) to
              load the full plain-language brief for this model.
            </p>
          )}
        </div>
      )}
    </article>
  );
}
