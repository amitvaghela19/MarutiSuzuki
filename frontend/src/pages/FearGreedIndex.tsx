import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchFearGreed,
  type FearGreedBulletin,
  type FearGreedEntity,
  type FearGreedPayload,
  type Snapshot,
} from "../api/client";
import FearGreedGauge from "../components/FearGreedGauge";
import FearGreedKnowledgePanel from "../components/FearGreedKnowledgePanel";
import KpiStrip from "../components/KpiStrip";
import PageHero from "../components/PageHero";
import SupplierNameLink from "../components/SupplierNameLink";
import { countryName } from "../utils/countries";
import { buildSupplierUrlMap, supplierReferenceUrl } from "../utils/supplierUrls";

type Props = {
  snapshot: Snapshot | null;
};

type BulletinFilter = "all" | "news" | "driver" | "macro";

const SEVERITY_CLASS: Record<string, string> = {
  critical: "high",
  high: "high",
  medium: "warn",
  low: "ok",
};

function bulletinForSupplier(
  bulletins: FearGreedBulletin[],
  supplier: FearGreedEntity
): FearGreedBulletin | undefined {
  const byEntity = bulletins.filter(
    (b) =>
      b.kind === "driver" &&
      b.detail.key_facts?.some(
        (f) => f.includes(supplier.name) || f.includes(supplier.id)
      )
  );
  if (byEntity.length) return byEntity[0];
  for (const d of supplier.drivers ?? []) {
    const match = bulletins.find((b) => b.kind === "driver" && b.title === d);
    if (match) return match;
  }
  const nameLower = supplier.name.toLowerCase();
  if (nameLower.includes("mrf") || nameLower.includes("tyre") || nameLower.includes("tire")) {
    return bulletins.find((b) => b.kind === "macro" && /mrf|tyre|tire|gulf/i.test(b.title));
  }
  if (nameLower.includes("gulf") || nameLower.includes("saudi") || nameLower.includes("uae")) {
    return bulletins.find((b) => b.kind === "macro" && /gulf|feedstock|rubber/i.test(b.title));
  }
  return bulletins.find((b) => b.kind === "driver");
}

export default function FearGreedIndex({ snapshot }: Props) {
  const [data, setData] = useState<FearGreedPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"fear" | "greed" | "name">("fear");
  const [bulletinFilter, setBulletinFilter] = useState<BulletinFilter>("all");
  const [selectedBulletin, setSelectedBulletin] = useState<FearGreedBulletin | null>(null);

  useEffect(() => {
    if (snapshot?.fear_greed) {
      setData(snapshot.fear_greed);
      return;
    }
    fetchFearGreed()
      .then(setData)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load"));
  }, [snapshot]);

  const bulletins = data?.bulletins ?? [];
  const hasBriefings = bulletins.length > 0;

  const supplierUrlMap = useMemo(
    () => buildSupplierUrlMap(snapshot?.suppliers),
    [snapshot?.suppliers]
  );

  const urlFor = useCallback(
    (entity: FearGreedEntity) =>
      supplierReferenceUrl(entity.id, supplierUrlMap, entity),
    [supplierUrlMap]
  );

  const openDriver = useCallback(
    (driverText: string, entityName: string) => {
      const candidates = bulletins.filter(
        (b) => b.kind === "driver" && b.title === driverText
      );
      const match =
        candidates.find((b) =>
          b.detail.key_facts?.some((f) => f.includes(entityName))
        ) ?? candidates[0];
      if (match) setSelectedBulletin(match);
    },
    [bulletins]
  );

  const openSupplierBriefing = useCallback(
    (supplier: FearGreedEntity) => {
      const match = bulletinForSupplier(bulletins, supplier);
      if (match) setSelectedBulletin(match);
    },
    [bulletins]
  );

  const suppliers = useMemo(() => {
    const list = [...(data?.suppliers || [])];
    if (sortBy === "fear") list.sort((a, b) => b.fear_index - a.fear_index);
    else if (sortBy === "greed") list.sort((a, b) => b.greed_index - a.greed_index);
    else list.sort((a, b) => a.name.localeCompare(b.name));
    return list;
  }, [data, sortBy]);

  const filteredBulletins = useMemo(() => {
    if (bulletinFilter === "all") return bulletins;
    return bulletins.filter((b) => b.kind === bulletinFilter);
  }, [bulletins, bulletinFilter]);

  if (err) return <div className="card glass">{err}</div>;
  if (!data) {
    return (
      <div className="card glass">
        <p>Loading Fear &amp; Greed indices…</p>
      </div>
    );
  }

  const m = data.maruti_suzuki;
  const avgFear =
    suppliers.length > 0
      ? suppliers.reduce((s, x) => s + x.fear_index, 0) / suppliers.length
      : 0;

  return (
    <>
      <PageHero
        title="Fear & Greed"
        subtitle="Heuristic supply-chain sentiment for Maruti Suzuki and tier-1 suppliers — refresh with Run analysis for live news and macro inputs"
        badge="Sentiment index"
      />

      <KpiStrip
        items={[
          { label: "MSIL fear", value: m.fear_index.toFixed(0), tone: "bad" },
          { label: "MSIL greed", value: m.greed_index.toFixed(0), tone: "ok" },
          { label: "OEM sentiment", value: m.sentiment_label, tone: "accent" },
          {
            label: "Suppliers",
            value: suppliers.length,
            hint: `Avg fear ${avgFear.toFixed(0)}`,
            tone: "accent",
          },
        ]}
      />

      {(data.disclaimer || data.scale_note) && (
        <p className="fg-meta muted">
          {data.disclaimer}
          {data.scale_note && <> · {data.scale_note}</>}
        </p>
      )}

      <div className="fg-hero card glass">
        <FearGreedGauge
          hero
          name={m.name}
          referenceUrl={urlFor(m)}
          subtitle={m.ticker ? `${m.ticker} · OEM` : "OEM"}
          fear={m.fear_index}
          greed={m.greed_index}
          label={m.sentiment_label}
          drivers={m.drivers}
          onDriverClick={hasBriefings ? (d) => openDriver(d, m.name) : undefined}
        />
        {hasBriefings && (
          <p className="fg-hero-hint muted">
            Click a driver below, a supplier card, or any briefing tile for the full panel.
          </p>
        )}
      </div>

      <div className="card glass fg-supplier-table-card">
        <div className="fg-toolbar">
          <h2>Supplier Fear &amp; Greed</h2>
          <label>
            Sort{" "}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            >
              <option value="fear">Highest fear</option>
              <option value="greed">Highest greed</option>
              <option value="name">Name</option>
            </select>
          </label>
        </div>
        <p className="muted fg-table-hint">
          {hasBriefings
            ? "Click supplier name for website ↗; click row elsewhere for briefing."
            : "Click supplier name for website ↗ when a public link is configured."}
        </p>
        <div className="table-scroll">
          <table className="fg-supplier-table">
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Country</th>
                <th>Exposure</th>
                <th>Fear</th>
                <th>Greed</th>
                <th>Sentiment</th>
                {hasBriefings && <th aria-label="Briefing" />}
              </tr>
            </thead>
            <tbody>
              {suppliers.map((s) => {
                const canBrief = hasBriefings && Boolean(bulletinForSupplier(bulletins, s));
                return (
                  <tr
                    key={s.id}
                    className={canBrief ? "fg-row-clickable" : undefined}
                    onClick={canBrief ? () => openSupplierBriefing(s) : undefined}
                    onKeyDown={
                      canBrief
                        ? (e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              openSupplierBriefing(s);
                            }
                          }
                        : undefined
                    }
                    tabIndex={canBrief ? 0 : undefined}
                    role={canBrief ? "button" : undefined}
                  >
                    <td className="fg-supplier-name-cell">
                      <SupplierNameLink name={s.name} referenceUrl={urlFor(s)} />
                      <br />
                      <code className="muted">{s.id}</code>
                    </td>
                    <td>{s.country_name || countryName(s.country)}</td>
                    <td>{s.part_exposure_weight?.toFixed(1) ?? "—"}%</td>
                    <td>
                      <span className="fg-inline meter-fear-inline">
                        {s.fear_index.toFixed(0)}
                      </span>
                    </td>
                    <td>
                      <span className="fg-inline meter-greed-inline">
                        {s.greed_index.toFixed(0)}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`badge fg-badge-${s.sentiment_label.toLowerCase().replace(/\s+/g, "-")}`}
                      >
                        {s.sentiment_label}
                      </span>
                    </td>
                    {hasBriefings && (
                      <td className="fg-row-briefing-cell">
                        {canBrief ? (
                          <button
                            type="button"
                            className="fg-row-briefing-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              openSupplierBriefing(s);
                            }}
                          >
                            Briefing →
                          </button>
                        ) : (
                          <span className="muted small">—</span>
                        )}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <section className="fg-supplier-grid-section">
        <h2 className="fg-section-title">Supplier gauges</h2>
        <p className="muted fg-section-sub">
          Compact fear/greed cards — open drivers or use <strong>Full briefing</strong> when
          available.
        </p>
        <div className="fg-supplier-grid">
          {suppliers.map((s) => {
            const canBrief = hasBriefings && Boolean(bulletinForSupplier(bulletins, s));
            return (
              <FearGreedGauge
                key={s.id}
                compact
                name={s.name}
                referenceUrl={urlFor(s)}
                subtitle={`${s.country_name || countryName(s.country)} · ${s.part_exposure_weight?.toFixed(0) ?? 0}% parts exposure`}
                fear={s.fear_index}
                greed={s.greed_index}
                label={s.sentiment_label}
                drivers={s.drivers}
                onDriverClick={
                  hasBriefings ? (d) => openDriver(d, s.name) : undefined
                }
                onOpenBriefing={canBrief ? () => openSupplierBriefing(s) : undefined}
              />
            );
          })}
        </div>
      </section>

      {hasBriefings && (
        <div className="card glass fg-bulletins-section">
          <div className="fg-toolbar">
            <h2>News &amp; briefings</h2>
            <label>
              Filter{" "}
              <select
                value={bulletinFilter}
                onChange={(e) =>
                  setBulletinFilter(e.target.value as BulletinFilter)
                }
              >
                <option value="all">All ({bulletins.length})</option>
                <option value="news">
                  Headlines ({bulletins.filter((b) => b.kind === "news").length})
                </option>
                <option value="driver">
                  Drivers ({bulletins.filter((b) => b.kind === "driver").length})
                </option>
                <option value="macro">
                  Strategic ({bulletins.filter((b) => b.kind === "macro").length})
                </option>
              </select>
            </label>
          </div>
          <p className="muted">
            Select a card for the full briefing panel — fear/greed impact, MSIL context, and
            what to watch.
          </p>
          <div className="fg-bulletin-grid">
            {filteredBulletins.map((b) => (
              <button
                key={b.id}
                type="button"
                className={`fg-bulletin-card glass${
                  selectedBulletin?.id === b.id ? " fg-bulletin-card--active" : ""
                }`}
                onClick={() => setSelectedBulletin(b)}
              >
                <div className="fg-bulletin-card-head">
                  <span className={`badge ${SEVERITY_CLASS[b.severity_label || "medium"]}`}>
                    {b.severity_label || b.kind}
                  </span>
                  <span className="badge">{b.kind}</span>
                </div>
                <h3>{b.title}</h3>
                <p className="fg-bulletin-teaser">{b.teaser}</p>
                <span className="fg-bulletin-cta">Read full briefing →</span>
              </button>
            ))}
          </div>
          {filteredBulletins.length === 0 && (
            <p className="muted">No bulletins in this filter.</p>
          )}
        </div>
      )}

      <FearGreedKnowledgePanel
        bulletin={selectedBulletin}
        onClose={() => setSelectedBulletin(null)}
      />
    </>
  );
}
