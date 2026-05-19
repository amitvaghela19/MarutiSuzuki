import type { TireDisruptionBrief } from "../api/client";

type Props = {
  brief: TireDisruptionBrief;
  onNavigateParts?: () => void;
  onNavigateScenario?: () => void;
};

const STRESS_CLASS: Record<string, string> = {
  low: "ok",
  elevated: "warn",
  high: "high",
};

export default function TireDisruptionCallout({
  brief,
  onNavigateParts,
  onNavigateScenario,
}: Props) {
  return (
    <div className="tire-spotlight glass">
      <div className="tire-spotlight-head">
        <h3>{brief.headline}</h3>
        <span className={`badge ${STRESS_CLASS[brief.stress_level] || "warn"}`}>
          {brief.stress_level}
        </span>
      </div>
      <p className="disclaimer">{brief.disclaimer}</p>
      <p>{brief.summary}</p>
      {brief.bullets.length > 0 && (
        <ul className="tire-spotlight-bullets">
          {brief.bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ul>
      )}
      {brief.news_hits.length > 0 && (
        <>
          <h4>Related headlines (ingest)</h4>
          <ul className="tire-spotlight-news">
            {brief.news_hits.map((n, i) => (
              <li key={`${i}-${n.title.slice(0, 20)}`}>
                <strong>{n.title}</strong>
                {n.summary && <p className="muted">{n.summary}</p>}
              </li>
            ))}
          </ul>
        </>
      )}
      <div className="tire-spotlight-actions">
        {onNavigateParts && (
          <button type="button" className="btn-ghost" onClick={onNavigateParts}>
            Open {brief.part_name} in Parts →
          </button>
        )}
        {onNavigateScenario && brief.related_scenario_id && (
          <button type="button" className="btn-ghost" onClick={onNavigateScenario}>
            Run Gulf tyre scenario →
          </button>
        )}
      </div>
    </div>
  );
}
