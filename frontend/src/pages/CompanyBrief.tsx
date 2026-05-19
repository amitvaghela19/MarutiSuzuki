import { useEffect, useState } from "react";
import { fetchCompanyProfile, type CompanyProfile } from "../api/client";

export default function CompanyBrief() {
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchCompanyProfile()
      .then(setProfile)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  if (err) return <div className="card">{err}</div>;
  if (!profile) return <div className="card">Loading company profile…</div>;

  const metrics = profile.key_metrics_demo || {};

  return (
    <>
      <div className="card hero-card">
        <h2>{profile.name}</h2>
        {profile.tagline && <p className="tagline">{profile.tagline}</p>}
        <p>
          <strong>Parent:</strong> {profile.parent_group} · <strong>HQ:</strong>{" "}
          {profile.headquarters} · <strong>Founded:</strong> {profile.founded}
        </p>
        {profile.ticker && (
          <p>
            <span className="badge ok">{profile.ticker}</span>
          </p>
        )}
        <p>{profile.role}</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Business model</h3>
          <ul>
            {(profile.business_model || []).map((b) => (
              <li key={b}>{b}</li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h3>Illustrative metrics (demo)</h3>
          <ul>
            {Object.entries(metrics).map(([k, v]) => (
              <li key={k}>
                <strong>{k.replace(/_/g, " ")}:</strong> {String(v)}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <h3>Manufacturing footprint</h3>
        <table>
          <thead>
            <tr>
              <th>Location</th>
              <th>Focus</th>
            </tr>
          </thead>
          <tbody>
            {(profile.manufacturing_footprint || []).map((m) => (
              <tr key={m.name}>
                <td>{m.name}</td>
                <td>{m.focus}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Product highlights</h3>
          <ul className="chip-list">
            {(profile.product_highlights || []).map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h3>Supply chain themes</h3>
          <ul>
            {(profile.supply_chain_themes || []).map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
      </div>

      {profile.disclaimer && (
        <p className="disclaimer">{profile.disclaimer}</p>
      )}
    </>
  );
}
