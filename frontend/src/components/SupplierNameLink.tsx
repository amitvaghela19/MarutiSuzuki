import type { MouseEvent } from "react";

type Props = {
  name: string;
  referenceUrl?: string | null;
  className?: string;
};

/** Supplier display name — opens public homepage/category URL when configured. */
export default function SupplierNameLink({ name, referenceUrl, className }: Props) {
  if (!referenceUrl?.trim()) {
    return <strong className={className}>{name}</strong>;
  }

  const stopRowActivate = (e: MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <a
      href={referenceUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`supplier-home-link${className ? ` ${className}` : ""}`}
      title="Open supplier site in a new tab"
      onClick={stopRowActivate}
    >
      <strong>{name}</strong>
      <span className="supplier-home-link-icon" aria-hidden>
        ↗
      </span>
    </a>
  );
}
