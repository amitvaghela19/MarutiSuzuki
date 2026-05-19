export type KpiItem = {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "ok" | "warn" | "bad" | "accent";
  onClick?: () => void;
};

export default function KpiStrip({ items }: { items: KpiItem[] }) {
  if (!items.length) return null;
  return (
    <div className="kpi-strip">
      {items.map((k) => (
        <div
          key={k.label}
          className={`kpi-tile tone-${k.tone || "accent"}${k.onClick ? " kpi-tile-clickable" : ""}`}
          role={k.onClick ? "button" : undefined}
          tabIndex={k.onClick ? 0 : undefined}
          onClick={k.onClick}
          onKeyDown={
            k.onClick
              ? (e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    k.onClick?.();
                  }
                }
              : undefined
          }
        >
          <span className="kpi-label">{k.label}</span>
          <span className="kpi-value">{k.value}</span>
          {k.hint && <span className="kpi-hint">{k.hint}</span>}
        </div>
      ))}
    </div>
  );
}
