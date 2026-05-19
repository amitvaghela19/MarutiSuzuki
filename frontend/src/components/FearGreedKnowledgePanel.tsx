import { useEffect } from "react";
import type { FearGreedBulletin } from "../api/client";

type Props = {
  bulletin: FearGreedBulletin | null;
  onClose: () => void;
};

const SEVERITY_CLASS: Record<string, string> = {
  critical: "high",
  high: "high",
  medium: "warn",
  low: "ok",
};

const KIND_LABEL: Record<string, string> = {
  news: "News headline",
  driver: "Index driver",
  macro: "Strategic bulletin",
};

export default function FearGreedKnowledgePanel({ bulletin, onClose }: Props) {
  useEffect(() => {
    if (!bulletin) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [bulletin, onClose]);

  if (!bulletin) return null;

  const d = bulletin.detail;
  const sev = bulletin.severity_label || "medium";

  return (
    <div
      className="fg-knowledge-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Fear and Greed briefing"
      onClick={onClose}
    >
      <article
        className="fg-knowledge-card glass"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="fg-knowledge-head">
          <button
            type="button"
            className="fg-knowledge-close"
            onClick={onClose}
            aria-label="Close briefing"
            title="Close (Esc)"
          >
            ×
          </button>
          <div className="fg-knowledge-badges">
            <span className={`badge ${SEVERITY_CLASS[sev] || "warn"}`}>{sev}</span>
            <span className="badge">{KIND_LABEL[bulletin.kind] || bulletin.kind}</span>
            {bulletin.risk_type && (
              <span className="badge warn">{bulletin.risk_type.replace(/_/g, " ")}</span>
            )}
          </div>
          <h2>{bulletin.title}</h2>
          {bulletin.published_at && (
            <p className="muted small">{new Date(bulletin.published_at).toLocaleString()}</p>
          )}
        </header>

        <p className="fg-knowledge-lede">{d.overview}</p>

        <section className="fg-knowledge-section">
          <h3>How this affects Fear</h3>
          <p>{d.fear_impact}</p>
        </section>

        <section className="fg-knowledge-section">
          <h3>How this affects Greed</h3>
          <p>{d.greed_impact}</p>
        </section>

        <section className="fg-knowledge-section fg-knowledge-msil">
          <h3>Why it matters for Maruti Suzuki supply chain</h3>
          <p>{d.msil_supply_chain}</p>
        </section>

        {d.key_facts && d.key_facts.length > 0 && (
          <section className="fg-knowledge-section">
            <h3>Key facts</h3>
            <ul className="fg-knowledge-facts">
              {d.key_facts.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </section>
        )}

        <section className="fg-knowledge-section">
          <h3>What to watch next</h3>
          <ul className="fg-knowledge-watch">
            {d.what_to_watch.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </section>

        {bulletin.source_url && (
          <p className="fg-knowledge-source">
            <a href={bulletin.source_url} target="_blank" rel="noopener noreferrer">
              Open source: {bulletin.source_label || "article"} →
            </a>
          </p>
        )}

        <p className="disclaimer small">
          Educational demo text — indices are heuristic, not exchange Fear & Greed or MSIL guidance.
        </p>

        <footer className="fg-knowledge-footer">
          <button type="button" className="btn-secondary fg-knowledge-close-btn" onClick={onClose}>
            Close briefing
          </button>
        </footer>
      </article>
    </div>
  );
}
