import { useState } from "react";
import AIHub from "./AIHub";
import DigitalTwin from "./DigitalTwin";
import PageHero from "../components/PageHero";
import type { Snapshot } from "../api/client";

type Tab = "ai" | "twin";

type Props = { snapshot: Snapshot | null };

export default function Intelligence({ snapshot }: Props) {
  const [tab, setTab] = useState<Tab>("ai");

  return (
    <>
      <PageHero
        title="AI & digital twin"
        subtitle="Model fleet registry and synthetic plant telemetry mesh"
        badge="Intelligence layer"
      />
      <div className="page-subtabs" role="tablist">
        <button
          type="button"
          role="tab"
          className={tab === "ai" ? "active" : ""}
          onClick={() => setTab("ai")}
        >
          AI fleet
        </button>
        <button
          type="button"
          role="tab"
          className={tab === "twin" ? "active" : ""}
          onClick={() => setTab("twin")}
        >
          Digital twin
        </button>
      </div>
      {tab === "ai" ? (
        <AIHub snapshot={snapshot} embedded />
      ) : (
        <DigitalTwin snapshot={snapshot} embedded />
      )}
    </>
  );
}
