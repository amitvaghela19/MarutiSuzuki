export type CitedBullet = {
  text: string;
  source_url?: string | null;
  source_label?: string | null;
};

export function normalizeBullets(
  items: (string | CitedBullet)[] | undefined
): CitedBullet[] {
  if (!items) return [];
  return items.map((item) => {
    if (typeof item === "string") return { text: item };
    return {
      text: item.text,
      source_url: item.source_url,
      source_label: item.source_label,
    };
  });
}

type Props = {
  items: (string | CitedBullet)[] | undefined;
};

export default function CitedBulletList({ items }: Props) {
  const bullets = normalizeBullets(items);
  return (
    <ul className="cited-list">
      {bullets.map((b) => (
        <li key={`${b.text}-${b.source_url || ""}`}>
          {b.source_url ? (
            <a
              href={b.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="bullet-link"
              title={b.source_label || "Open source"}
            >
              {b.text}
              <span className="link-hint" aria-hidden="true">
                ↗
              </span>
            </a>
          ) : (
            b.text
          )}
          {b.source_url && b.source_label && (
            <span className="source-label">{b.source_label}</span>
          )}
        </li>
      ))}
    </ul>
  );
}
