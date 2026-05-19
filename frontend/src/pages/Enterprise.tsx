import { useEffect, useState } from "react";
import CompanyBrief from "./CompanyBrief";
import StrategicAnalysis from "./StrategicAnalysis";
import PageHero from "../components/PageHero";
import DisruptionTimeline from "../components/DisruptionTimeline";
import {
  fetchDisruptionHistory,
  type DisruptionHistoryPayload,
  type Snapshot,
} from "../api/client";

type Tab = "brief" | "strategic" | "history";

type Props = {
  snapshot: Snapshot | null;
};

export default function Enterprise({ snapshot }: Props) {
  const [tab, setTab] = useState<Tab>("brief");
  const [history, setHistory] = useState<DisruptionHistoryPayload | null>(
    snapshot?.disruption_history ?? null
  );

  useEffect(() => {
    if (snapshot?.disruption_history) {
      setHistory(snapshot.disruption_history);
      return;
    }
    fetchDisruptionHistory()
      .then(setHistory)
      .catch(() => {});
  }, [snapshot?.disruption_history, snapshot?.run_id]);

  return (
    <>
      <PageHero
        title="Enterprise intelligence"
        subtitle="Maruti Suzuki company brief, strategic SWOT / PESTLE, and public disruption history"
        badge="MSIL context"
      />
      <div className="page-subtabs" role="tablist">
        <button
          type="button"
          role="tab"
          className={tab === "brief" ? "active" : ""}
          onClick={() => setTab("brief")}
        >
          Company brief
        </button>
        <button
          type="button"
          role="tab"
          className={tab === "strategic" ? "active" : ""}
          onClick={() => setTab("strategic")}
        >
          SWOT &amp; PESTLE
        </button>
        <button
          type="button"
          role="tab"
          className={tab === "history" ? "active" : ""}
          onClick={() => setTab("history")}
        >
          Disruption history
        </button>
      </div>
      {tab === "brief" && <CompanyBrief />}
      {tab === "strategic" && <StrategicAnalysis />}
      {tab === "history" && (
        <div className="card glass">
          <h2>Supply-chain disruption history</h2>
          <p className="muted">
            Publicly reported episodes that shaped Maruti Suzuki production and sourcing.
            Run analysis to see which episodes rhyme with today&apos;s simulated stress.
          </p>
          {history ? (
            <DisruptionTimeline history={history} />
          ) : (
            <p className="muted">Loading timeline…</p>
          )}
          <p className="muted small disruption-footnote">
            2024 production trims reported as dealer inventory management are omitted here
            as they were demand-led, not supplier failure.
          </p>
        </div>
      )}
    </>
  );
}
