import { useState } from "react";
import type { Snapshot } from "../api/client";
import SupplierExplorer from "./SupplierExplorer";
import SupplierSourcing from "./SupplierSourcing";
import PageHero from "../components/PageHero";

type Tab = "directory" | "matrix";

type Props = {
  snapshot: Snapshot | null;
  onOpenWhy: (partId: string) => void;
};

export default function Suppliers({ snapshot, onOpenWhy }: Props) {
  const [tab, setTab] = useState<Tab>("directory");

  return (
    <>
      <PageHero
        title="Suppliers"
        subtitle="IndiaMART-style discovery, trust tiers, sourcing matrix, and alternates"
        badge="33 partners"
      />
      <div className="page-subtabs" role="tablist">
        <button
          type="button"
          role="tab"
          className={tab === "directory" ? "active" : ""}
          onClick={() => setTab("directory")}
        >
          Directory &amp; SWOT
        </button>
        <button
          type="button"
          role="tab"
          className={tab === "matrix" ? "active" : ""}
          onClick={() => setTab("matrix")}
        >
          Sourcing matrix
        </button>
      </div>
      {tab === "directory" ? (
        <SupplierExplorer snapshot={snapshot} onOpenWhy={onOpenWhy} />
      ) : (
        <SupplierSourcing snapshot={snapshot} onOpenWhy={onOpenWhy} />
      )}
    </>
  );
}
