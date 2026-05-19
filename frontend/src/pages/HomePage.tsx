import type { Snapshot } from "../api/client";
import SuvHeroImage from "../components/SuvHeroImage";

type TabId =
  | "dashboard"
  | "intelligence"
  | "enterprise"
  | "scenarios"
  | "parts"
  | "suppliers";

type Props = {
  snapshot: Snapshot | null;
  loading: boolean;
  onRunAnalysis: () => void;
  onNavigate: (tab: TabId) => void;
  onOpenCritical?: () => void;
};

const QUICK_LINKS: { id: TabId; title: string; desc: string; icon: string }[] = [
  {
    id: "dashboard",
    title: "Command center",
    desc: "Signals, critical news, risks & recommendations",
    icon: "◈",
  },
  {
    id: "intelligence",
    title: "AI & digital twin",
    desc: "Model fleet and plant telemetry mesh",
    icon: "◇",
  },
  {
    id: "enterprise",
    title: "Brief & strategy",
    desc: "Company profile, SWOT & PESTLE with citations",
    icon: "▣",
  },
  {
    id: "scenarios",
    title: "Scenario lab",
    desc: "Stress-test shocks and dual-source strategies",
    icon: "⚡",
  },
  {
    id: "parts",
    title: "Parts catalog",
    desc: "Full catalog with suppliers & alternates",
    icon: "⚙",
  },
  {
    id: "suppliers",
    title: "Suppliers",
    desc: "Directory, sourcing matrix & Fear/Greed",
    icon: "⊞",
  },
];

export default function HomePage({
  snapshot,
  loading,
  onRunAnalysis,
  onNavigate,
  onOpenCritical,
}: Props) {
  const hasRun = Boolean(snapshot);
  const critical = snapshot?.command_signals?.critical_count ?? 0;

  return (
    <div className="home-page">
      <section className="home-hero glass">
        <div className="home-hero-copy">
          <span className="hero-badge">Maruti Suzuki · Supply chain AI</span>
          <h1 className="home-title">
            Orchestrate your network from{" "}
            <span className="text-gradient">orbit</span>
          </h1>
          <p className="home-lead">
            A futuristic command center for parts risk, supplier intelligence,
            digital twin plants, and scenario simulation — built as a demo POC
            for India&apos;s largest passenger vehicle maker.
          </p>
          <div className="home-cta-row">
            <button
              type="button"
              className="btn-primary"
              onClick={onRunAnalysis}
              disabled={loading}
            >
              {loading ? "Running pipeline…" : hasRun ? "Re-run analysis" : "Run analysis"}
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => onNavigate("dashboard")}
            >
              Open command center →
            </button>
          </div>
          {hasRun && critical > 0 && (
            <p className="home-run-meta">
              <button
                type="button"
                className="critical-cta-link"
                onClick={() => (onOpenCritical ? onOpenCritical() : onNavigate("dashboard"))}
              >
                {critical} critical signal{critical > 1 ? "s" : ""} — view details
              </button>
            </p>
          )}
          {hasRun && critical === 0 && (
            <p className="muted home-run-meta">
              Last run {new Date(snapshot!.generated_at).toLocaleString()}
            </p>
          )}
        </div>
        <SuvHeroImage />
      </section>

      <section className="home-quick-grid">
        {QUICK_LINKS.map((link) => (
          <button
            key={link.id}
            type="button"
            className="home-quick-card glass"
            onClick={() => onNavigate(link.id)}
          >
            <span className="home-quick-icon">{link.icon}</span>
            <strong>{link.title}</strong>
            <span className="muted">{link.desc}</span>
          </button>
        ))}
      </section>

      <section className="card glass home-stats">
        <h2>Platform capabilities</h2>
        <ul className="home-cap-list">
          <li>33 suppliers with IndiaMART-style discovery tiers</li>
          <li>11 Monte Carlo scenarios · 3 sourcing strategies</li>
          <li>Fear &amp; Greed indices for MSIL and each supplier</li>
          <li>SWOT &amp; PESTLE with cited public sources</li>
          <li>Clickable ops signals with &quot;why&quot; explanations</li>
        </ul>
        <p className="disclaimer">
          Homepage 3D SUV is a community Vitara Brezza model (CC Attribution, BHP3D /
          REVOLZ MODDING on Sketchfab), not an official Maruti Suzuki asset.
        </p>
      </section>
    </div>
  );
}
