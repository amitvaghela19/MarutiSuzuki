import type { ReactNode } from "react";

type Props = {
  title: string;
  subtitle?: string;
  badge?: string;
  children?: ReactNode;
};

export default function PageHero({ title, subtitle, badge, children }: Props) {
  return (
    <header className="page-hero glass">
      <div>
        {badge && <span className="hero-badge">{badge}</span>}
        <h1>{title}</h1>
        {subtitle && <p className="hero-subtitle">{subtitle}</p>}
      </div>
      {children && <div className="hero-actions">{children}</div>}
    </header>
  );
}
