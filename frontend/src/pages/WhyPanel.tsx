import type { Snapshot } from "../api/client";
import { countryName } from "../utils/countries";

type Props = {
  snapshot: Snapshot | null;
  selectedPartId: string | null;
  onSelectPart: (id: string) => void;
  asDrawer?: boolean;
  onClose?: () => void;
};

function supplierLabel(snapshot: Snapshot, id: string): string {
  const sup = snapshot.suppliers?.find((s) => s.id === id);
  return sup ? `${sup.name} (${id})` : id;
}

export default function WhyPanel({
  snapshot,
  selectedPartId,
  onSelectPart,
  asDrawer,
  onClose,
}: Props) {
  const content = !snapshot ? (
    <p>Run analysis first.</p>
  ) : (
    <>
      <label>
        Part:{" "}
        <select
          value={selectedPartId || ""}
          onChange={(e) => onSelectPart(e.target.value)}
        >
          <option value="">Select part</option>
          {snapshot.recommendations.map((r) => (
            <option key={r.part_id} value={r.part_id}>
              {r.part_name}
            </option>
          ))}
        </select>
      </label>
      {selectedPartId && (
        <>
          {(() => {
            const rec = snapshot.recommendations.find((r) => r.part_id === selectedPartId);
            const ranks = snapshot.part_rankings[selectedPartId] || {};
            const sourcing = snapshot.sourcing_matrix?.parts.find(
              (p) => p.part_id === selectedPartId
            );
            if (!rec) return <p>No recommendation for this part.</p>;
            const rationale = rec.rationale as Record<string, unknown>;
            return (
              <>
                {sourcing && (
                  <>
                    <h3>Main supplier</h3>
                    <p>
                      {sourcing.primary_supplier?.name} (
                      {countryName(
                        sourcing.primary_supplier?.country,
                        sourcing.primary_supplier?.country_name
                      )}
                    </p>
                    <h3>Approved alternates</h3>
                    <ul>
                      {sourcing.alternate_suppliers.map((s) => (
                        <li key={s.id}>
                          {s.name} ({countryName(s.country, s.country_name)})
                        </li>
                      ))}
                    </ul>
                  </>
                )}
                <h3>
                  Recommended allocation
                  {typeof rationale.allocation_mode === "string" && (
                    <span className="badge ok" style={{ marginLeft: "0.5rem" }}>
                      {String(rationale.allocation_mode).replace(/_/g, " ")}
                    </span>
                  )}
                </h3>
                <ul>
                  {Object.entries(rec.allocation).map(([sup, pct]) => (
                    <li key={sup}>
                      {supplierLabel(snapshot, sup)}: {(pct * 100).toFixed(0)}%
                    </li>
                  ))}
                </ul>
                <h3>TOPSIS ranks (1 = best)</h3>
                <ul>
                  {Object.entries(ranks)
                    .sort((a, b) => a[1] - b[1])
                    .map(([sup, rank]) => (
                      <li key={sup}>
                        {supplierLabel(snapshot, sup)}: rank {rank}
                      </li>
                    ))}
                </ul>
                {(rec.alternative_solutions?.length ||
                  sourcing?.alternative_solutions.length) && (
                  <>
                    <h3>Alternative solutions</h3>
                    <ul>
                      {(rec.alternative_solutions || sourcing?.alternative_solutions || []).map(
                        (sol) => (
                          <li key={sol}>{sol}</li>
                        )
                      )}
                    </ul>
                  </>
                )}
                {Array.isArray(rationale.drivers) && rationale.drivers.length > 0 && (
                  <>
                    <h3>Why this split</h3>
                    <ul>
                      {(rationale.drivers as string[]).map((d) => (
                        <li key={d}>{d}</li>
                      ))}
                    </ul>
                  </>
                )}
              </>
            );
          })()}
        </>
      )}
    </>
  );

  if (asDrawer) {
    return (
      <aside className="drawer">
        <button type="button" onClick={onClose} style={{ float: "right" }}>
          Close
        </button>
        <h2>Why</h2>
        {content}
      </aside>
    );
  }

  return (
    <div className="card">
      <h2>Why Panel</h2>
      {content}
    </div>
  );
}
