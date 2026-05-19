type Item = { title: string; severity?: number };

type Props = {
  items: Item[];
  onItemClick?: (index: number) => void;
};

export default function LiveTicker({ items, onItemClick }: Props) {
  if (!items.length) return null;
  const doubled = [...items, ...items];
  return (
    <div className="live-ticker" aria-label="Live headlines">
      <span className="ticker-label">LIVE</span>
      <div className="ticker-track">
        {doubled.map((n, i) => {
          const index = i % items.length;
          const content = (
            <>
              {n.title}
              {n.severity != null && n.severity >= 4 && (
                <span className="ticker-sev-badge"> critical</span>
              )}
            </>
          );
          if (onItemClick) {
            return (
              <button
                key={`${i}-${n.title.slice(0, 20)}`}
                type="button"
                className="ticker-item ticker-item-btn"
                onClick={() => onItemClick(index)}
              >
                {content}
              </button>
            );
          }
          return (
            <span key={`${i}-${n.title.slice(0, 20)}`} className="ticker-item">
              {content}
            </span>
          );
        })}
      </div>
    </div>
  );
}
