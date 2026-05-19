# Reuse prompt — build a similar supply-chain command center for another company

Copy the block below into a **new Cursor chat** when you want a project like this repo (Maruti Suzuki Supply Chain Command Center) but for a **different company, industry, or country**.

Fill in every `[BRACKET]` before sending. Delete sections you do not need.

---

## Master prompt (copy from here)

```
Build a full-stack "Supply Chain Command Center" web application modeled on the same architecture and feature set as my reference project: a FastAPI + React (Vite + TypeScript) demo POC with YAML-driven config, one-click "Run analysis" pipeline, snapshot JSON, and polished dark/light UI.

## Target company & scope

- **Company:** [e.g. Tata Motors / Reliance Retail / Boeing / Unilever India]
- **Ticker / market (if any):** [e.g. NSE: TATAMOTORS]
- **Industry:** [e.g. automotive OEM / FMCG / aerospace]
- **Headquarters / key plants:** [e.g. Pune, Jamshedpur, Sanand]
- **Hero positioning line:** [e.g. "Orchestrate your retail network from orbit"]
- **Disclaimer:** Educational demo POC — NOT affiliated with or using proprietary data from [Company]. Synthetic suppliers unless public citations.

## Signature storyline (optional but recommended)

Pick ONE narrative thread professors can follow (like MRF/Gulf tyres in the Maruti project):

- **Theme:** [e.g. lithium battery / cocoa supply / semiconductor fab / cold-chain pharma]
- **Hero suppliers (2–4 names):** [public archetypes only]
- **Hero part SKU:** [e.g. PART-BATTERY-PACK]
- **Hero scenario ID:** [e.g. CN-RARE-EARTH-SHOCK]
- **Regions to stress:** [e.g. CN, CL, AU — ISO country codes]

## Technical requirements (keep same stack unless I say otherwise)

- **Backend:** Python 3.11+, FastAPI, uvicorn, Pydantic, DuckDB, pytest
- **Frontend:** React 18, TypeScript, Vite, Framer Motion where appropriate
- **Analytics:** NumPy, SimPy (Monte Carlo), TOPSIS MCDM, rule-based news classifier
- **AI chat:** Ollama (configurable model), streaming SSE, snapshot-grounded context + optional live RSS/Yahoo enrichment
- **Data ingest:** World Bank, GDELT, RSS (required); FRED optional via env key
- **Tasks:** PowerShell `tasks.ps1` for install, migrate, backend, frontend, test (Windows-first)
- **Persistence:** `data/snapshots/latest.json` + DuckDB run history; cache under `data/cache/`

## Features to implement (same as reference — do not drop unless I strike through)

1. **App shell:** Sidebar nav, global header with "Run analysis" + run pill, live news ticker, KPI strip, dark/light theme
2. **Home:** Hero image area, quick links, critical-signal CTA after first run
3. **Command center:** Ops signals feed, news spotlight, country/commodity/supplier risk lists, recommendations, signature disruption callout, signal detail drawer
4. **Brief & strategy:** Company brief, SWOT/PESTLE with cited bullets, public disruption history timeline
5. **Parts catalog:** Categories, criticality, suppliers, enriched risk after run, "Why" drawer trigger
6. **Suppliers:** Directory (trust tiers, reference_url links), sourcing matrix + mitigation playbooks
7. **Fear & Greed:** OEM + supplier indices (0–100), drivers, bulletin cards, full-screen knowledge panel with close/Esc
8. **Scenario lab:** 10–15 YAML scenarios × single/dual/emergency strategies, results table + heatmap
9. **AI & twin:** Demo model fleet cards + synthetic digital-twin plant mesh
10. **Why panel:** TOPSIS criteria table, allocation rationale, scenario stockout drivers
11. **Supply-chain chat:** Floating resizable panel, localStorage size, grounded on latest snapshot

## Configuration (YAML in `config/`)

Generate and wire:

- `suppliers.yaml` — [N] suppliers with country (ISO-2), lead_time_days, cost_index, commodities, trust_tier, reference_url
- `parts.yaml` — [M] parts with criticality 1–5, supplier_ids, alternative_solutions
- `scenarios.yaml` — include BASELINE + themed shocks aligned to signature storyline
- `mcdm.yaml`, `thresholds.yaml`, `news_keywords.yaml`, `data_sources.yaml`
- `[company]_company.yaml` — company brief
- `strategic_analysis.yaml`, `supplier_strategic.yaml`, `supply_disruptions_history.yaml`
- `ai_models.yaml`, `plants.yaml`

Document tuning in `docs/CONFIG_GUIDE.md`.

## Documentation deliverables (required at end)

Create/update all of these with the new company name:

1. **README.md** — GitHub-ready: badges, features, architecture mermaid, project tree, quick start, API table, disclaimer
2. **storytelling.md** — Narrative chapter-by-chapter walkthrough of every feature
3. **website.md** — Per-page component reference + system architecture
4. **explanation.md** — Viva guide: what/why/where every number comes from (country codes, lead time, Fear/Greed formulas, traceability table)
5. **docs/ARCHITECTURE.md**, **docs/DATA_SOURCES.md** — keep in sync

## Quality bar

- Match reference UX polish: glass cards, consistent spacing, PageHero, KpiStrip patterns
- All formulas documented in `explanation.md` with file paths and weights
- `npm run build` and `pytest` must pass
- No proprietary [Company] data; cite public URLs only for company brief bullets
- E2E: at least one Playwright flow for "Run analysis" if reference has e2e/

## What to reuse vs rewrite

- **Reuse patterns** from reference: pipeline order, snapshot shape, App.tsx tab routing, fear_greed.py weight structure, allocation.py threshold logic
- **Rewrite content** for new company: all YAML names, scenarios, news keywords, hero copy, images path `frontend/public/images/hero-[slug].webp`

## Out of scope (unless I ask)

- Production auth, multi-tenant ERP integration, real-time plant SCADA
- Deploy to cloud (local dev only unless I request Docker)

Start by scanning the reference repo structure, then scaffold the new project [in this folder / in a new folder named [PROJECT_FOLDER]]. Confirm the company storyline with me before writing 35 suppliers.
```

---

## Short prompt (minimal)

Use when you already have this repo open and want a **fork-style** rebrand:

```
Rebrand this Supply Chain Command Center from Maruti Suzuki to [COMPANY NAME].

- Update all YAML in config/, hero copy, company brief, disruption history, and signature storyline to: [ONE SENTENCE THEME].
- Replace tyre/MRF/Gulf narrative with: [NEW NARRATIVE].
- Keep stack, pipeline, pages, and docs structure identical.
- Regenerate README, storytelling.md, website.md, explanation.md for [COMPANY].
- Run tests and frontend build; fix any broken references.
```

---

## Checklist before you send the master prompt

| Item | Example |
|------|---------|
| Company legal name | Maruti Suzuki India Limited |
| Public website | https://www.marutisuzuki.com/ |
| ~20–40 parts categories | braking, powertrain, EV battery… |
| ~25–40 demo suppliers | mix home country + import corridors |
| 1 memorable crisis thread | Gulf tyres, chips, cocoa, lithium |
| Professor needs formulas doc? | Yes → insist on `explanation.md` |
| Ollama model | deepseek-r1:latest or llama3 |
| Repo folder name | `TataMotors-SCC` |

---

## Optional add-ons (append to master prompt)

**More suppliers / parts**

```
Increase to 50 suppliers and 30 parts; add categories [list].
```

**Different industry (retail / pharma)**

```
Parts = SKUs; suppliers = distributors; scenarios = port strike, cold-chain failure, API shortage.
```

**No AI chat**

```
Skip Ollama integration; remove SupplyChainChat and chat routes.
```

**GitHub publish**

```
After build passes, prepare README for GitHub and list secrets needed in .env.example only (no real keys).
```

**Professor viva pack only**

```
I already have the app; write only explanation.md and a 2-page PDF-style summary from snapshot formulas.
```

---

## Reference

This prompt was written for the **Maruti Suzuki Supply Chain Command Center** repository.  
See root [README.md](../README.md), [explanation.md](../explanation.md), and [website.md](../website.md) for the target quality and scope.
