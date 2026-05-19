import type { DisruptionHistoryPayload } from "../api/client";

type Props = {
  history: DisruptionHistoryPayload;
  compact?: boolean;
  maxItems?: number;
};

const CATEGORY_LABEL: Record<string, string> = {
  labor: "Labor",
  pandemic: "Pandemic",
  commodity: "Commodity",
  geopolitical: "Geopolitical",
};

export default function DisruptionTimeline({
  history,
  compact = false,
  maxItems,
}: Props) {
  const incidents = maxItems
    ? history.incidents.slice(0, maxItems)
    : history.incidents;

  return (
    <div className={`disruption-timeline${compact ? " disruption-timeline--compact" : ""}`}>
      {history.disclaimer && (
        <p className="disclaimer disruption-disclaimer">{history.disclaimer}</p>
      )}
      {!compact && history.timeline_summary && (
        <p className="muted disruption-summary">{history.timeline_summary}</p>
      )}
      <ol className="disruption-timeline-list">
        {incidents.map((inc) => (
          <li key={inc.id} className="disruption-card glass">
            <div className="disruption-card-year">
              <span>{inc.year}</span>
              {inc.live_analog && (
                <span className="badge high disruption-analog-badge">
                  Rhymes with today&apos;s run
                </span>
              )}
            </div>
            <div className="disruption-card-body">
              <div className="disruption-card-head">
                <h3>{inc.title}</h3>
                <span className="badge">
                  {CATEGORY_LABEL[inc.category] || inc.category}
                </span>
              </div>
              <p>{inc.summary}</p>
              {!compact && (
                <>
                  <h4>What MSIL felt</h4>
                  <ul>
                    {(inc.impact_bullets || []).map((b) => (
                      <li key={b}>{b}</li>
                    ))}
                  </ul>
                  {inc.supply_chain_lesson && (
                    <p className="why-box">
                      <strong>Lesson:</strong> {inc.supply_chain_lesson}
                    </p>
                  )}
                </>
              )}
              {inc.source_url && (
                <a
                  href={inc.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="disruption-source-link"
                >
                  Source: {inc.source_label || "Public report"} →
                </a>
              )}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
