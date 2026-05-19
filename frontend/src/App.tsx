import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchLatestSnapshot, runAnalysis, type Snapshot } from "./api/client";
import NeuralBackground from "./components/NeuralBackground";
import LiveTicker from "./components/LiveTicker";
import KpiStrip, { type KpiItem } from "./components/KpiStrip";
import PartsCatalog from "./pages/PartsCatalog";
import Dashboard from "./pages/Dashboard";
import ScenarioLab from "./pages/ScenarioLab";
import WhyPanel from "./pages/WhyPanel";
import FearGreedIndex from "./pages/FearGreedIndex";
import HomePage from "./pages/HomePage";
import Enterprise from "./pages/Enterprise";
import Intelligence from "./pages/Intelligence";
import Suppliers from "./pages/Suppliers";
import SupplyChainChat from "./components/SupplyChainChat";

type Tab =
  | "home"
  | "dashboard"
  | "enterprise"
  | "parts"
  | "suppliers"
  | "feargreed"
  | "scenarios"
  | "intelligence";

type NavItem = { id: Tab; label: string; icon: string };
type NavGroup = { title: string; items: NavItem[] };

const NAV: NavGroup[] = [
  {
    title: "Command",
    items: [
      { id: "home", label: "Home", icon: "⌂" },
      { id: "dashboard", label: "Command center", icon: "◈" },
      { id: "intelligence", label: "AI & twin", icon: "◇" },
    ],
  },
  {
    title: "Enterprise",
    items: [{ id: "enterprise", label: "Brief & strategy", icon: "▣" }],
  },
  {
    title: "Supply chain",
    items: [
      { id: "parts", label: "Parts catalog", icon: "⚙" },
      { id: "suppliers", label: "Suppliers", icon: "⊞" },
      { id: "feargreed", label: "Fear & Greed", icon: "◐" },
      { id: "scenarios", label: "Scenario lab", icon: "⚡" },
    ],
  },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [whyPart, setWhyPart] = useState<string | null>(null);
  const [dashFocus, setDashFocus] = useState<{
    severity?: string | null;
    signalId?: string | null;
  } | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    if (typeof window === "undefined") return "dark";
    return (localStorage.getItem("mscc-theme") as "dark" | "light") || "dark";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("mscc-theme", theme);
  }, [theme]);

  const refresh = useCallback(async () => {
    try {
      const s = await fetchLatestSnapshot();
      setSnapshot(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load snapshot");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const onRunAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const s = await runAnalysis();
      setSnapshot(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const goToDashboard = useCallback((severity?: string | null, signalId?: string | null) => {
    setTab("dashboard");
    setDashFocus({ severity: severity ?? null, signalId: signalId ?? null });
  }, []);

  const handleSignalNavigate = useCallback(
    (target: string, entityId?: string | null) => {
      if (target === "why" && entityId) {
        setWhyPart(entityId);
        return;
      }
      if (target === "scenarios") setTab("scenarios");
      else if (target === "suppliers") setTab("suppliers");
      else if (target === "parts") setTab("parts");
      else if (target === "dashboard") goToDashboard();
      else setTab("dashboard");
    },
    [goToDashboard]
  );

  const globalKpis = useMemo((): KpiItem[] => {
    if (!snapshot) return [];
    const parts =
      snapshot.parts?.length ??
      Object.values(snapshot.parts_by_category || {}).flat().length;
    const signals = snapshot.command_signals;
    const twin = snapshot.digital_twin;
    const ai = snapshot.ai_models;
    const signalTone: KpiItem["tone"] = signals?.critical_count ? "bad" : "ok";
    const twinTone: KpiItem["tone"] =
      twin?.network_health === "green" ? "ok" : "warn";
    return [
      { label: "Parts tracked", value: parts, tone: "accent" },
      {
        label: "Suppliers",
        value: snapshot.suppliers?.length ?? "—",
        tone: "accent",
      },
      {
        label: "Ops signals",
        value: signals?.total ?? 0,
        hint: signals?.critical_count
          ? `${signals.critical_count} critical — click to view`
          : "Click to open signals",
        tone: signalTone,
        onClick: () =>
          goToDashboard(signals?.critical_count ? "critical" : "all"),
      },
      {
        label: "AI fleet",
        value: ai?.summary.fleet_health ?? "—",
        tone: "accent",
        onClick: () => setTab("intelligence"),
      },
      {
        label: "Twin network",
        value: twin?.network_health ?? "—",
        tone: twinTone,
        onClick: () => setTab("intelligence"),
      },
    ];
  }, [snapshot, goToDashboard]);

  const headlines = snapshot?.news_headlines ?? [];

  return (
    <div className="app-shell">
      <NeuralBackground />
      <aside className="sidebar glass">
        <div className="sidebar-brand">
          <span className="brand-mark">MS</span>
          <div>
            <strong>Command Center</strong>
            <span className="muted">Supply chain AI</span>
          </div>
        </div>
        {NAV.map((group) => (
          <div key={group.title} className="nav-group">
            <span className="nav-group-title">{group.title}</span>
            {group.items.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${tab === item.id ? "active" : ""}`}
                onClick={() => {
                  setTab(item.id);
                  if (item.id !== "dashboard") setDashFocus(null);
                }}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        ))}
        <div className="sidebar-footer">
          <button
            type="button"
            className="btn-ghost"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? "☀ Light mode" : "☾ Dark mode"}
          </button>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-header glass">
          <div>
            <h1>Maruti Suzuki Supply Chain Command Center</h1>
            <p className="subtitle">
              Futuristic POC — AI models, digital twin, scenarios & trusted sourcing
            </p>
          </div>
          <div className="header-actions">
            {snapshot && (
              <span className="run-pill">
                Run {snapshot.run_id.slice(0, 8)} ·{" "}
                {new Date(snapshot.generated_at).toLocaleString()}
              </span>
            )}
            <button
              type="button"
              className="btn-primary"
              data-testid="run-analysis-btn"
              onClick={onRunAnalysis}
              disabled={loading}
            >
              {loading ? "Running pipeline…" : "Run analysis"}
            </button>
          </div>
        </header>

        {headlines.length > 0 && (
          <LiveTicker
            items={headlines}
            onItemClick={(index) => {
              const sig = snapshot?.command_signals?.signals.find(
                (s) => s.category === "news" && s.news_index === index
              );
              goToDashboard(sig?.severity ?? "all", sig?.id ?? null);
            }}
          />
        )}
        {globalKpis.length > 0 && <KpiStrip items={globalKpis} />}

        <main className="page-content">
          {error && (
            <div className="card glass alert-card">
              {error}
            </div>
          )}
          {tab === "home" && (
            <HomePage
              snapshot={snapshot}
              loading={loading}
              onRunAnalysis={onRunAnalysis}
              onNavigate={(t) => setTab(t as Tab)}
              onOpenCritical={() => goToDashboard("critical")}
            />
          )}
          {tab === "enterprise" && <Enterprise snapshot={snapshot} />}
          {tab === "parts" && (
            <PartsCatalog snapshot={snapshot} onOpenWhy={setWhyPart} />
          )}
          {tab === "suppliers" && (
            <Suppliers snapshot={snapshot} onOpenWhy={setWhyPart} />
          )}
          {tab === "feargreed" && <FearGreedIndex snapshot={snapshot} />}
          {tab === "dashboard" && (
            <Dashboard
              snapshot={snapshot}
              onOpenWhy={setWhyPart}
              onNavigate={handleSignalNavigate}
              focusSeverity={dashFocus?.severity}
              focusSignalId={dashFocus?.signalId}
            />
          )}
          {tab === "intelligence" && <Intelligence snapshot={snapshot} />}
          {tab === "scenarios" && <ScenarioLab snapshot={snapshot} />}
        </main>
      </div>

      {whyPart && (
        <WhyPanel
          snapshot={snapshot}
          selectedPartId={whyPart}
          onSelectPart={setWhyPart}
          asDrawer
          onClose={() => setWhyPart(null)}
        />
      )}

      <SupplyChainChat snapshot={snapshot} />
    </div>
  );
}
