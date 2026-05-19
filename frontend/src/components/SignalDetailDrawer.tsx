import type { CommandSignal, NewsHeadline } from "../api/client";

type Props = {
  signal: CommandSignal | null;
  news?: NewsHeadline | null;
  onClose: () => void;
  onNavigate?: (tab: string, entityId?: string | null) => void;
};

function newsSeverityLabel(raw?: number): string {
  if (!raw) return "low";
  if (raw >= 5) return "critical";
  if (raw >= 4) return "high";
  if (raw >= 2) return "medium";
  return "low";
}

function buildNewsWhy(n: NewsHeadline): string {
  const parts = [
    `Classified as ${(n.risk_type || "general").replace(/_/g, " ")} risk (severity ${n.severity ?? "?"}/5).`,
  ];
  if (n.summary) parts.push(n.summary);
  if (n.country_code) parts.push(`Geography hint: ${n.country_code}.`);
  return parts.join(" ");
}

const severityClass: Record<string, string> = {
  critical: "high",
  high: "high",
  medium: "warn",
  low: "ok",
};

export default function SignalDetailDrawer({
  signal,
  news,
  onClose,
  onNavigate,
}: Props) {
  if (!signal && !news) return null;

  const title = signal?.title ?? news?.title ?? "Signal";
  const severity = signal?.severity ?? newsSeverityLabel(news?.severity);
  const category = signal?.category ?? "news";
  const why =
    signal?.why ??
    (news ? buildNewsWhy(news) : "No explanation available for this item.");
  const summary = signal?.summary ?? news?.summary;
  const detail = signal?.detail;
  const navigateTo = signal?.navigate_to;
  const entityId = signal?.entity_id;

  return (
    <aside className="drawer signal-detail-drawer" aria-label="Signal details">
      <button type="button" className="btn-ghost drawer-close" onClick={onClose}>
        Close
      </button>
      <div className="signal-detail-head">
        <span className={`badge ${severityClass[severity] || "warn"}`}>{severity}</span>
        <span className="signal-category">{category}</span>
        {signal?.priority != null && (
          <span className="signal-priority">P{signal.priority}</span>
        )}
      </div>
      <h2>{title}</h2>
      {detail && <p className="muted">{detail}</p>}
      <div className="why-box">
        <strong>Why this matters</strong>
        <p>{why}</p>
      </div>
      {summary && summary !== why && (
        <p className="signal-summary muted">{summary}</p>
      )}
      {news?.url && (
        <p>
          <a href={news.url} target="_blank" rel="noreferrer" className="bullet-link">
            Open source article
          </a>
        </p>
      )}
      {navigateTo && onNavigate && (
        <button
          type="button"
          className="btn-primary"
          onClick={() => {
            onNavigate(navigateTo, entityId);
            onClose();
          }}
        >
          {signal?.action ?? "Go to related view"}
        </button>
      )}
    </aside>
  );
}
