import SupplierNameLink from "./SupplierNameLink";

type Props = {
  name: string;
  subtitle?: string;
  referenceUrl?: string | null;
  fear: number;
  greed: number;
  label: string;
  drivers?: string[];
  compact?: boolean;
  hero?: boolean;
  onDriverClick?: (driver: string, entityName: string) => void;
  onOpenBriefing?: () => void;
};

export default function FearGreedGauge({
  name,
  subtitle,
  referenceUrl,
  fear,
  greed,
  label,
  drivers,
  compact,
  hero,
  onDriverClick,
  onOpenBriefing,
}: Props) {
  const labelClass = label.toLowerCase().replace(/\s+/g, "-");
  const driverInteractive = Boolean(onDriverClick);
  const showDrivers = drivers && drivers.length > 0 && (!compact || driverInteractive);

  return (
    <div
      className={`fg-card${compact ? " fg-card-compact" : ""}${hero ? " fg-card-hero" : ""}${onOpenBriefing ? " fg-card-interactive" : ""}`}
    >
      <div className="fg-card-head">
        <h3 className="fg-card-title">
          <SupplierNameLink name={name} referenceUrl={referenceUrl} />
        </h3>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      <p className={`fg-sentiment fg-sentiment-${labelClass}`}>{label}</p>
      <div className="fg-meters">
        <div className="fg-row">
          <span className="fg-row-label">Fear</span>
          <div className="meter meter-fear">
            <span style={{ width: `${Math.min(100, fear)}%` }} />
          </div>
          <span className="fg-value">{fear.toFixed(0)}</span>
        </div>
        <div className="fg-row">
          <span className="fg-row-label">Greed</span>
          <div className="meter meter-greed">
            <span style={{ width: `${Math.min(100, greed)}%` }} />
          </div>
          <span className="fg-value">{greed.toFixed(0)}</span>
        </div>
      </div>
      {showDrivers && (
        <ul
          className={`fg-drivers${hero ? " fg-drivers-hero" : ""}${compact ? " fg-drivers-compact" : ""}`}
        >
          {drivers!.map((d) => (
            <li key={d}>
              {driverInteractive ? (
                <button
                  type="button"
                  className="fg-driver-btn"
                  onClick={() => onDriverClick!(d, name)}
                >
                  {d}
                </button>
              ) : (
                d
              )}
            </li>
          ))}
        </ul>
      )}
      {onOpenBriefing && (
        <button type="button" className="fg-card-briefing-cta" onClick={onOpenBriefing}>
          Full briefing →
        </button>
      )}
    </div>
  );
}
