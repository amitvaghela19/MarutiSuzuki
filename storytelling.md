# Storytelling — The Maruti Suzuki Supply Chain Command Center

*A narrative guide to every capability in this project. Read this when you want the “why” and the journey, not just the install steps.*

---

## Prologue: Monday morning at the command desk

Imagine you are the supply-chain director for **Maruti Suzuki India Limited (MSIL)**. It is Monday, 8:47 AM. Gurgaon and Manesar are running, but your phone already has three tabs open: a rubber futures chart, a Red Sea shipping headline, and a tier-1 supplier escalation from Chennai.

You do not need another PowerPoint. You need a **single orbit** — one screen that answers:

- What is breaking *right now*?
- Which **parts** and **suppliers** are exposed?
- If the Gulf corridor stutters again, what happens to **tyres** on the line?
- What should sourcing do **this week**?

That is the story this application tells.

---

## Chapter 1 — The one button that changes everything

### “Run analysis”

At the top of every page sits **Run analysis**. It is not cosmetic. It is the ignition key for the entire backend **pipeline**:

1. **Listen to the world** — macro indicators, news wires, commodity proxies  
2. **Score the network** — countries, commodities, 35 suppliers  
3. **Rank choices** — TOPSIS multi-criteria decision-making per part  
4. **Stress-test** — SimPy simulations across 13 scenarios and 3 sourcing strategies  
5. **Publish a snapshot** — one JSON artifact the whole UI shares  

When the run completes, a pill appears: `Run 50373b22 · 17 May 2026, 14:32`. Every KPI, signal, gauge, and chat answer can now cite **that** moment in time.

**Story beat:** The demo is honest about being synthetic, but the *workflow* mirrors how real command centers freeze a “decision baseline” after each planning cycle.

---

## Chapter 2 — Home: the invitation to orbit

**Route:** `Home` tab (`HomePage.tsx`)

The landing page is deliberately cinematic:

- A **hero SUV image** (`SuvHeroImage`) anchors the brand — Maruti as mobility, not spreadsheets  
- Copy positions the product: *“Orchestrate your network from orbit”*  
- **Quick links** teleport you to Command center, AI & twin, Brief & strategy, Scenario lab, Parts, Suppliers  
- If a run exists and critical signals are present, a **critical alert strip** offers one-click jump to filtered signals  

**Why it matters:** Executives land here; analysts skip straight to Command center. Both paths are valid.

---

## Chapter 3 — Command center: the beating heart

**Route:** `Command center` tab (`Dashboard.tsx`)

This is the operational **war room**.

### Global context (always visible when a snapshot exists)

- **Live ticker** — scrolling headlines from the latest ingest; click a headline to jump to its matching ops signal  
- **KPI strip** — parts tracked, supplier count, ops signal total (clickable), AI fleet health, twin network health  

### Inside the dashboard

| Section | Story |
|---------|--------|
| **Ops Pulse summary** | Autopilot mode, critical/high counts — “what needs a human now” |
| **Signal feed** | Prioritized cards: severity, category, priority, detail, navigation targets |
| **News spotlight** | Headlines linked to signals; severity badges from classifier |
| **MRF / Gulf tyre watch** | `TireDisruptionCallout` — stress level, bullets, link to parts |
| **Disruption history teaser** | Episodes that “rhyme” with current sim stress |
| **Risk lists** | Top countries, commodities, suppliers as bar charts |
| **Recommendations** | Parts with allocation %, primary/alternate suppliers, **Why** buttons |

### The signal drawer

Click a signal → `SignalDetailDrawer` slides in with full text, suggested actions, and links to scenarios, suppliers, or parts.

**Story beat:** A planner sees “Gulf tyre shock — stockout P=100%” in signals, clicks through to Scenario lab, then opens **Why** on `PART-TIRE` to see TOPSIS ranks. That is the intended click path.

---

## Chapter 4 — Enterprise intelligence: who we are, what shaped us

**Route:** `Brief & strategy` (`Enterprise.tsx` — three subtabs)

### 4a. Company brief (`CompanyBrief.tsx`)

Public-information synthesis of MSIL:

- Business model, plants (Gurgaon, Manesar, Gujarat expansion)  
- Product highlights (Swift, Brezza, etc.)  
- Supply-chain themes (localization, chips, rubber/Gulf routes, EV)  
- Demo metrics with disclaimer  

### 4b. SWOT & PESTLE (`StrategicAnalysis.tsx`)

Structured strategic analysis with **cited bullets** (`CitedBulletList`):

- MSIL-level SWOT and PESTLE  
- Archetype partners (not proprietary supplier lists)  
- Search/filter for long documents  

### 4c. Disruption history (`DisruptionTimeline.tsx`)

A timeline of **real public episodes**:

| Year | Episode | Lesson |
|------|---------|--------|
| 2011 | Labor unrest | Supplier concentration risk |
| 2020 | COVID lockdown | Restart harder than shutdown |
| 2021–22 | Chip shortage | Electronics = board-level risk |
| 2026 (demo) | MRF / Gulf tyre watch | Regional shock → Indian OEM tyres |

After **Run analysis**, episodes can flag `live_analog: true` when simulated stress matches their scenario link (e.g. `ME-GULF-TIRE`).

**Story beat:** History is not decoration — it explains *why* the Gulf tyre scenario exists in config.

---

## Chapter 5 — Parts catalog: the BOM as a living map

**Route:** `Parts catalog` (`PartsCatalog.tsx`)

Every part is a character in the story:

- **Category filters** — braking, powertrain, electrical, body, etc.  
- **Criticality** — 1–5 stars; 5 = line-stop potential  
- **Main supplier** and **alternates** from config + post-run enrichment  
- **Risk overlay** after analysis (supplier scores, allocation mode)  
- **“Why”** opens the drawer — TOPSIS ranks, drivers, dual-source triggers  

Featured storyline: **`PART-TIRE`** — OEM tyre set tied to MRF-class OEM, ASEAN rubber corridors, Gulf feedstock.

---

## Chapter 6 — Suppliers: trust, discovery, and the matrix

**Route:** `Suppliers` (`Suppliers.tsx` — two subtabs)

### 6a. Directory & SWOT (`SupplierExplorer.tsx`)

- **35 suppliers** with country, city, commodities, lead time  
- **Trust tiers:** OEM tier-1, ACMA cluster, IndiaMART-verified  
- **Reference URLs** — click supplier name → MRF website or IndiaMART category (public discovery, not endorsement)  
- Post-run: risk score, Fear/Greed fear/greed columns  
- Selecting a row shows strategic blurbs from `supplier_strategic.yaml`  

### 6b. Sourcing matrix (`SupplierSourcing.tsx`)

For each part:

- Primary vs alternate suppliers  
- **Allocation percentages** from recommendations  
- **Mitigation playbooks** — e.g. CEAT/Apollo swap, ASEAN corridor, emergency tyre bank  

**Story beat:** Directory answers “who are they?”; matrix answers “how do we survive if they fail?”

---

## Chapter 7 — Fear & Greed: sentiment, not stock tickers

**Route:** `Fear & Greed` (`FearGreedIndex.tsx`)

Inspired by market Fear & Greed indices, but **redefined for supply chains**:

- **Fear (0–100)** — risk, news pressure, simulation stockout stress  
- **Greed (0–100)** — stability, capability, positive drivers  
- **Sentiment label** — Extreme Fear → Extreme Greed  

### Layers of the page

1. **MSIL hero gauge** — OEM aggregate; clickable drivers open briefings  
2. **Supplier table** — sortable; row click → briefing; name click → website  
3. **Supplier gauge grid** — compact cards with drivers + “Full briefing →”  
4. **Bulletin cards** — news, driver, and macro briefings  
5. **Knowledge panel** — full-screen overlay: fear impact, greed impact, MSIL context, facts, what to watch; **×** or Esc to close  

**MRF / Gulf narrative:** When `tire_disruption_brief` is high stress, bullets cite MRF Tyres India, UAE/Saudi feedstock scores, and `ME-GULF-TIRE` stockout probability.

---

## Chapter 8 — Scenario lab: stress without stopping the line

**Route:** `Scenario lab` (`ScenarioLab.tsx`)

Thirteen scenarios from `scenarios.yaml`, including:

- `ME-GULF-TIRE` — Red Sea & Gulf petrochemical / MRF programmes  
- `RUBBER-SHOCK` — ASEAN export delay  
- `CHIP-SHORTAGE` — MCU allocation  
- `MONSOON-NCR` — Gurgaon–Manesar flooding  
- …and more  

Three **strategies** per scenario:

| Strategy | Meaning |
|----------|---------|
| `single_source` | Baseline dependency |
| `dual_source` | Split primary/alternate |
| `multi_source` | Adds tertiary where configured |

**Monte Carlo** runs produce `stockout_probability`, service level, recovery days. The UI offers catalog view, results tables, and a **matrix** heatmap.

**Story beat:** The Gulf tyre scenario is the dramatic set piece — often 100% stockout under single_source, motivating dual/multi allocation on `PART-TIRE`.

---

## Chapter 9 — AI & digital twin: the future layer

**Route:** `AI & twin` (`Intelligence.tsx`)

### AI fleet (`AIHub.tsx`)

Demo registry of ML/analytics “models”:

- Graph risk GNN, transformer news encoder, RL allocator, digital twin sync, MCDM engine…  
- Status: active / training; confidence; latency  
- **Expandable cards** (`ModelCard`) with newspaper-style reports after analysis  

### Digital twin (`DigitalTwin.tsx`)

Synthetic **plant mesh**:

- Gurgaon, Manesar, Gujarat nodes  
- Throughput, buffer, bottleneck hints  
- Network health badge (green / amber)  

**Story beat:** These layers say: “the command center is not only rules — it is the shell where real models would plug in.”

---

## Chapter 10 — Why panel: the explainer in the drawer

**Route:** Overlay (`WhyPanel.tsx`) — opened from parts, dashboard, suppliers

When you ask **Why** on a part:

- TOPSIS criteria scores per supplier  
- Rank order and weight sensitivity narrative  
- Allocation mode (`single` / `dual` / `multi`) and drivers  
- Max scenario stockout that triggered dual-source rules  

**Story beat:** Transparency — the UI shows its homework.

---

## Chapter 11 — Supply-chain chat: the analyst that read the snapshot

**Component:** `SupplyChainChat.tsx` (floating, all pages)

### How it works

1. User opens **💬** FAB  
2. Backend builds **system prompt** from `latest.json`: suppliers, tyre brief, sim results, signals, recommendations, disruption history  
3. **Live enrichment** (optional): Google News RSS + Yahoo Finance (`MRF.NS`, `MARUTI.NS`) + cached RSS  
4. **Ollama** streams DeepSeek R1 (or your configured model)  
5. Reasoning tags stripped from display  

### UX details

- Resizable panel (drag top-left grip); size saved in `localStorage`  
- **Reset size** / **Refresh** (Ollama status)  
- Starter prompts for common questions  
- Answers structured: Situation → Metrics → Actions → Watch  

**Story beat:** The chat is not a generic ChatGPT window — it is a **snapshot-grounded co-pilot**. Ask “What is MRF Gulf exposure?” and it should cite allocation %, Gulf scenario stockout P, and supplier risk scores — not hand-wave.

---

## Chapter 12 — The data fable (what happens under the hood)

### Ingest characters

| Character | Role |
|-----------|------|
| **World Bank** | GDP, inflation, trade openness → country risk |
| **GDELT** | Global news documentary API |
| **RSS** | BBC India/world, UN news — reliable free feeds |
| **FRED** | Rubber, metals, electronics PPI — optional key |

When APIs fail, **cache + demo fallbacks** keep the story moving (see `data/cache/`).

### Risk algebra (simplified)

- Supplier risk blends country, commodity, lead time, news severity  
- Recommendations compare TOPSIS rank vs scenario stockout thresholds  
- Fear & Greed reweights fear/greed legs per entity  

### Persistence

- `data/snapshots/<uuid>.json` — immutable run record  
- `data/snapshots/latest.json` — UI + chat read this  
- DuckDB — run history, health metadata  

---

## Chapter 13 — Configuration as screenwriting

YAML in `config/` is the **script**:

- Add a supplier → appears in directory, sim, Fear & Greed  
- Add a scenario shock → new row in Scenario lab  
- Tune `thresholds.yaml` → more dual-source recommendations  
- Extend `supply_disruptions_history.yaml` → new timeline card  

The pipeline does not require code changes for most demos — only YAML edits and re-run.

---

## Chapter 14 — Trust, disclaimers, and what we will not claim

Throughout the UI you will see:

- “Demo POC” / “Synthetic” / “Not proprietary MSIL data”  
- IndiaMART links as **category discovery**, not supplier endorsement  
- Fear & Greed ≠ NSE Fear & Greed Index  
- AI model cards = illustrative capabilities, not production model endpoints  

The story is credible **process**, not classified **data**.

---

## Epilogue: who this impresses

| Audience | Takeaway |
|----------|----------|
| **Recruiter / portfolio** | Full-stack + data pipeline + polished UI |
| **Supply-chain class** | Risk, MCDM, simulation, dual-sourcing in one app |
| **MSIL-themed hackathon** | Brand-aware narrative (tyres, Gurgaon, Swift) |
| **Your future self** | A template for the next OEM command center |

You built an orbit. **Run analysis**, then read the story the data tells.

---

*For component-level UI detail and architecture diagrams, see [website.md](website.md). For viva-style “what is this / where did the number come from”, see [explanation.md](explanation.md). For clone-and-run instructions, see [README.md](README.md).*
