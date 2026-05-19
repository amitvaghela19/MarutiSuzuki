# explanation.md — Complete “why & where from” guide for your professor

Use this document when your professor asks **“What is this?”**, **“Why is it here?”**, or **“Where did this number come from?”**  
Every answer below ties **UI → backend formula → config file → data source**.

> **Note:** Filename is `explanation.md` (same file; spelling for search).  
> Companion docs: [README.md](README.md) (setup), [storytelling.md](storytelling.md) (narrative), [website.md](website.md) (components).

---

## How to answer in a viva (one sentence pattern)

> **“This is [WHAT]. I show it because [WHY for the user]. The value comes from [SOURCE], calculated in [FILE/FUNCTION] using [FORMULA or RULE], and it updates when I click Run analysis.”**

Example:

> **“TH is Thailand’s ISO country code. I show it so planners see geographic exposure. The label ‘Thailand’ comes from `country_name('TH')` in `backend/utils/countries.py`, and the risk score for Thailand is computed in `score_countries()` from World Bank macro + news hits tagged to TH.”**

---

## Part A — Abbreviations & codes (small questions)

### A.1 Country codes (IN, TH, AE, SA, JP, DE, KR, MY, …)

**What:** Two-letter codes from **ISO 3166-1 alpha-2** (international standard for countries).

**Why in the app:** Suppliers and news are tied to a **country** so we can aggregate macro risk, map headlines, and show “where exposure sits” on a map/table.

**Where shown:** Supplier directory, parts, risk lists, Fear & Greed drivers, scenario config (`countries: [AE, SA]`).

| Code | Country | Used in this project for |
|------|---------|---------------------------|
| **IN** | India | MSIL home market; most demo tier-1 suppliers; Maruti country risk |
| **TH** | Thailand | ASEAN rubber corridor (e.g. Siam Rubber Components) |
| **MY** | Malaysia | ASEAN elastomers (Penang) |
| **JP** | Japan | Suzuki global channel, precision parts, chips |
| **DE** | Germany | Metals / European logistics scenario |
| **KR** | South Korea | Electronics suppliers |
| **AE** | **United Arab Emirates** (not “AU”) | Gulf petrochemical / synthetic rubber feedstock |
| **SA** | Saudi Arabia | Carbon black / Gulf feedstock |
| **US**, **CN**, **GB** | USA, China, UK | Listed in `countries.py` for display if ever referenced |

**If professor says “AU”:**  
In *this* codebase we use **AE** for UAE. **AU** would mean **Australia** (ISO code). If you see “AU” on screen, it is likely a mis-read of **AE**, or a future supplier — check `config/suppliers.yaml` → `country:` field.

**How name appears:**  
`backend/utils/countries.py` maps code → full name. If code unknown, UI shows the raw code.

```python
# backend/utils/countries.py
COUNTRY_NAMES = {"IN": "India", "TH": "Thailand", "AE": "United Arab Emirates", ...}
```

---

### A.2 Supplier ID (e.g. `SUP-IN-TIRE`, `SUP-AE-GULF-CHEM`)

**What:** Internal **primary key** in YAML — not a real vendor ERP code.

**Pattern:** `SUP-{country}-{role}`  
**Why:** Stable link between parts, simulation, Fear & Greed, and chat context.

**Where defined:** `config/suppliers.yaml`

---

### A.3 Part ID (e.g. `PART-TIRE`, `PART-BRAKE-PAD`)

**What:** Internal BOM line identifier.

**Why:** Links MCDM ranking, recommendations, Why panel, and scenarios.

**Where defined:** `config/parts.yaml`, `config/parts_extra.yaml`

---

### A.4 `lead_time_days` (NOT Python `lead()`)

**What professors might confuse:**  
- **Lead time (supply chain)** = calendar days from **order release** to **delivery** at MSIL plant.  
- **Python `lead()`** = string method — **not used** in this project for scoring.

**Why in config:** Longer lead time = more exposure to disruption during transit/production → higher risk and higher **Fear**.

**Where set:** Each supplier in `config/suppliers.yaml`, e.g. `lead_time_days: 21`

**How it enters math:**

1. **Supplier risk** (`backend/analytics/risk.py`):

   ```
   lead_penalty = clamp(lead_time_days × 1.2, 0, 100)
   supplier_risk = 0.40×country_risk + 0.35×commodity_risk + 0.25×lead_penalty
   ```

2. **TOPSIS** (`backend/analytics/mcdm/engine.py`): criterion `lead_time`, direction **min** (shorter is better), weight **0.20** from `config/mcdm.yaml`.

3. **Fear index** (`backend/analytics/fear_greed.py`):

   ```
   lead_fear = clamp(lead_time_days × 1.1)
   fear += 0.10 × lead_fear   (10% weight inside fear formula)
   ```

4. **MCDM gate:** Suppliers with `lead_time_days > 45` can be **disqualified** unless no one else passes (`max_lead_time_days: 45` in `mcdm.yaml`).

**Story you can tell:** “We model ASEAN rubber at 18–28 days and Gulf feedstock with longer effective lanes; if lead time exceeds 25 days, the Fear driver text says *Long lead time increases fear*.”

---

### A.5 `cost_index`

**What:** Demo **relative unit cost** (1.0 = baseline; lower is cheaper).

**Why:** TOPSIS **minimizes** cost; Fear/Greed **greed** rewards cost-competitive suppliers.

**Example:** `cost_index: 0.92` → cheaper than baseline → higher greed component `(1.2 - cost_index) × 55`.

**Not from live invoices** — authored in YAML for teaching.

---

### A.6 `criticality` (1–5 on parts)

**What:** How painful a stockout is (5 = line-stop, safety-related).

**Why:**  
- Weights supplier importance in Fear & Greed network (`part_exposure_weight`).  
- Pushes **dual/multi sourcing** in `allocation.py` when criticality ≥ 4.

**Where:** `config/parts.yaml` per part.

---

### A.7 Trust tiers (`oem_tier1`, `acma_cluster`, `indiamart_verified`)

**What:** Demo labels for supplier **trust / verification story**.

**Why:** Filter and explain sourcing desk narrative; IndiaMART links are **public discovery**, not MSIL approval.

**Where:** `config/suppliers.yaml` → `trust_tier`

---

### A.8 Strategies: `single_source`, `dual_source`, `emergency_airfreight`

**What:** Three **sourcing policies** tested in simulation.

| Strategy | Meaning in SimPy demo |
|----------|------------------------|
| **single_source** | One lane; baseline lead time & capacity |
| **dual_source** | Split volume; effective lead time reduced ~10%; capacity +18% |
| **emergency_airfreight** | Short lead time (×0.35), lower capacity, cost ×1.45 |

**Why:** Show trade-off: cost vs stockout probability.

**Where:** `backend/analytics/simulation.py` — 30 Monte Carlo runs per scenario×strategy.

---

### A.9 `stockout_probability`

**What:** Fraction of simulation runs (out of 30) where **at least one stockout** occurred.

**Example:** `1.0` = 100% of runs had a stockout → worst case for that strategy.

**How:** SimPy discrete-event model — production every `lead_time` days, consumption every day, inventory can hit zero.

**Not MSIL real OTIF** — illustrative.

---

### A.10 `TOPSIS` / MCDM

**What:** **Technique for Order Preference by Similarity to Ideal Solution** — multi-criteria ranking.

**Why:** Choose **best supplier** per part when many criteria conflict (cost vs risk vs lead time).

**Criteria & weights** (`config/mcdm.yaml`):

| Criterion | Direction | Weight |
|-----------|-----------|--------|
| cost | min | 0.25 |
| lead_time | min | 0.20 |
| country_risk | min | 0.25 |
| quality (ISO9001) | max | 0.15 |
| ev_ready | max | 0.15 |

**Code:** `backend/analytics/mcdm/topsis.py` + `engine.py`

**Output:** Rank 1 = best supplier for that part → becomes **primary** in recommendations.

---

### A.11 `run_id` / Run pill in header

**What:** UUID for one pipeline execution.

**Why:** Proves all numbers on screen are from the **same** analysis moment.

**Where stored:** `data/snapshots/<run_id>.json` and `latest.json`

---

### A.12 Other UI words

| Term | Meaning |
|------|---------|
| **POC** | Proof of concept — demo, not production |
| **MSIL** | Maruti Suzuki India Limited |
| **MRF** | MRF Tyres (India OEM tyre example in config) |
| **OEM** | Original equipment manufacturer (car maker) |
| **Tier-1** | Direct supplier to OEM |
| **ACMA** | Automotive Component Manufacturers Association (India) |
| **BOM** | Bill of materials (parts list) |
| **KPI** | Key performance indicator (tiles at top) |
| **SWOT / PESTLE** | Strategic analysis frameworks |
| **SimPy** | Python discrete-event simulation library |
| **Ollama** | Local LLM server for chatbot |
| **GDELT** | Global news database API |
| **FRED** | US Federal Reserve economic data (commodity proxies) |

---

## Part B — Fear & Greed percentages (most asked)

### B.1 What Fear and Greed mean **here**

**Not** the CNN stock market Fear & Greed Index.  
**Yes** a **0–100 demo index** for supply-chain **stress (Fear)** vs **confidence (Greed)**.

- **Fear ↑** = more worry (risk, news, long lead times, stockouts)  
- **Greed ↑** = more confidence (stability, cost advantage, capabilities)  
- **Label** (Extreme Fear … Extreme Greed) from **net = greed − fear**

```python
# backend/analytics/fear_greed.py — _sentiment_label
net = greed - fear
net ≤ -35  → Extreme Fear
net ≤ -12  → Fear
net ≤ 12   → Neutral
net ≤ 35   → Greed
else       → Extreme Greed
```

---

### B.2 Supplier-level **Fear** (0–100)

**Inputs:**

| Input | Source |
|-------|--------|
| `supplier_risk` | `score_suppliers()` in `risk.py` |
| `country_risk` | `score_countries()` for supplier’s `country` |
| `commodity_risk` | Average over supplier’s `commodities[]` |
| `lead_fear` | `clamp(lead_time_days × 1.1)` |
| `news_fear` | Sum of `severity × 8` for news with matching `country_code` |

**Formula (weights must sum to 1.0):**

```
fear = clamp(
    0.42 × supplier_risk
  + 0.22 × country_risk
  + 0.18 × commodity_risk
  + 0.10 × lead_fear
  + 0.08 × news_fear
)
```

**Why these weights:** Supplier composite dominates (42%); geography and commodities follow; lead time and news are **modifiers** (10% + 8%).

**Drivers (text bullets):** Rule-based, e.g. if `supplier_risk ≥ 70` → “Elevated composite supplier risk”.

---

### B.3 Supplier-level **Greed** (0–100)

```
cost_greed = clamp((1.2 - cost_index) × 55)
stability = clamp(100 - supplier_risk)
cap_bonus = 8 if ev_ready else 0; +6 if tier1

greed = clamp(
    0.38 × stability
  + 0.28 × cost_greed
  + 0.20 × (100 - commodity_risk)
  + 0.14 × (100 - country_risk)
  + cap_bonus
)
```

**Story:** Greed rewards **low risk**, **low cost index**, **safe commodities/country**, and **EV/tier-1 flags**.

---

### B.4 Maruti Suzuki (OEM) aggregate Fear & Greed

**Fear:**

```
weighted_fear = Σ (supplier_risk[s] × part_exposure_weight[s])
part_exposure_weight[s] = sum of part criticality for parts using s / normalized

maruti_fear = clamp(
    0.35 × weighted_fear
  + 0.25 × country_risk['IN']
  + 0.20 × maruti_news_pressure
  + 0.20 × max_stockout × 100
)
```

- `maruti_news_pressure`: headlines mentioning maruti/suzuki/msil × severity × 10  
- `max_stockout`: worst `stockout_probability` across all sim results (0–1), ×100 for scale  

**Greed:**

```
maruti_greed = clamp(
    0.40 × average(supplier greed indices)
  + 0.30 × (100 - maruti_fear)
  + 0.20 × (100 - max_stockout×100)
  + 0.10 × (100 - country_risk['IN'])
)
```

**Why:** OEM row is a **portfolio view** — network risk + India macro + auto news + simulation stress.

---

### B.5 `part_exposure_weight` (e.g. 12.4%)

**What:** How much of the **parts portfolio** (by criticality) touches that supplier.

**Formula:**

```
For each supplier s:
  weight[s] = Σ (part.criticality) for all parts where s in part.supplier_ids
Normalize so Σ weight[s] = 1
Display = weight[s] × 100  (percent)
```

**Why shown:** Professor can ask “why is MRF big on Fear page?” — because `PART-TIRE` has high criticality and ties to `SUP-IN-TIRE`.

---

## Part C — Where other major numbers come from

### C.1 Country risk score (0–100)

**File:** `backend/analytics/risk.py` → `score_countries()`

**Steps:**

1. Load World Bank indicators per country (`config/data_sources.yaml` countries list).  
2. `macro_risk` from GDP/inflation series (heuristic if data thin → ~50).  
3. `event_density = clamp(news_count_for_country × 12)`.  
4. `score = 0.55×macro_risk + 0.45×event_density`

**News country tag:** From `news_keywords.yaml` rules → `country_hints: [TH, MY]` etc.

---

### C.2 Commodity risk score (0–100)

**File:** `score_commodities()`

- **Volatility** from FRED price series (if available): std/mean × 200, capped.  
- **News hits** if commodity name in headline or `risk_type == commodity`.  
- `score = 0.6×vol_risk + 0.4×news_risk`

---

### C.3 Supplier risk score (0–100)

**File:** `score_suppliers()`

```
lead_penalty = clamp(lead_time_days × 1.2)
score = clamp(0.4×country_risk + 0.35×commodity_risk + 0.25×lead_penalty)
```

Displayed on: Dashboard risk list, supplier table, parts enrichment.

---

### C.4 News severity (1–5)

**File:** `backend/ingestion/news_classifier.py`

**Rule-based** (not ML): scan title+summary for keywords in `config/news_keywords.yaml`.

Example:

```yaml
- keywords: [rubber, mrf, tyre, tire]
  severity: 3
  risk_type: commodity
  country_hints: [TH, MY, IN]
```

**Highest matching rule wins** (`severity = max(...)`).

**Mapped to UI signal severity** in `command_signals.py` (e.g. 5 → critical).

---

### C.5 Allocation percentages (e.g. MRF 72% / alternate 28%)

**File:** `backend/analytics/allocation.py` → `compute_part_allocation()`

**Not fixed 60/40.** Depends on:

| Threshold | Value (`config/thresholds.yaml`) |
|-----------|----------------------------------|
| `stockout_probability_limit` | 0.25 |
| `high_risk` | 70 |
| `emergency_override` | 85 |

**Logic summary:**

1. If max stockout ≤ 25% **and** primary risk < 70 → **100% primary** (single source).  
2. Else if stockout high → dual split; primary % between ~55–82% from formula.  
3. If primary risk ≥ 85 → **emergency_shift** (more volume to alternate).  
4. Criticality ≥ 4 + high stockout + 2 alternates → optional **third** supplier (multi_source).  
5. If alternate share < 8% → collapse back to single source.

**Why:** Numbers change per part because **criticality**, **risks**, and **simulation** differ.

---

### C.6 Service level % (simulation)

```
service_level_pct = 100 × (1 - stockout_days / horizon_days)
```

90-day horizon by default in scenario config.

---

### C.7 Digital twin numbers (throughput, OEE, buffer days)

**File:** `backend/analytics/digital_twin.py`

**Synthetic:** Derived from `hash(run_id + plant_id)` so they **change each run** but look realistic.

**Why:** Illustrate where a real MES/SCADA feed would plug in — not live plant data.

---

### C.8 AI model “confidence” / latency

**File:** `backend/analytics/ai_hub.py`

**Demo registry** from `config/ai_models.yaml`, enriched with snapshot-aware **report paragraphs** after pipeline.

**Why:** Show how ML microservices would appear in a command center UI.

---

## Part D — Screen-by-screen: what it is, why it exists

### D.1 Global shell (every page)

| Element | What | Why | Data source |
|---------|------|-----|-------------|
| **Sidebar** | Navigation | Group features by planner mental model | Static `NAV` in `App.tsx` |
| **Run analysis** | Runs pipeline | One button = reproducible snapshot | `POST /api/run-analysis` |
| **Run pill** | Run id + timestamp | Audit trail | `snapshot.run_id`, `generated_at` |
| **Live ticker** | Scrolling news | Situational awareness | `news_headlines` (top 10) |
| **KPI strip** | 5 tiles | At-a-glance health | Counts from snapshot |
| **Theme toggle** | Dark/light | Accessibility | `localStorage` |
| **💬 Chat** | Q&A | Explain snapshot in natural language | Ollama + `latest.json` context |

---

### D.2 Home

| Element | Why |
|---------|-----|
| SUV hero | Brand context (Maruti = vehicles, not abstract data) |
| Quick links | Onboarding — where to click first |
| Critical alert | If `critical_count > 0`, push user to Command center |

---

### D.3 Command center (Dashboard)

| Element | Why |
|---------|-----|
| Ops Pulse | Summarize signal counts |
| Signal feed | Prioritized to-do list for planners |
| News spotlight | Link media to structured signals |
| Tire/MRF callout | Highlight configured storyline (Gulf + tyres) |
| Disruption timeline teaser | Connect today’s stress to history |
| Risk lists (country/commodity/supplier) | Top offenders from `risk.py` |
| Recommendations | Actionable sourcing splits |
| Signal drawer | Deep dive + navigation |

---

### D.4 Brief & strategy (Enterprise)

| Subtab | Why |
|--------|-----|
| Company brief | Who MSIL is (plants, products) — context for non-automotive professors |
| SWOT/PESTLE | Strategic frameworks with **citations** (`CitedBulletList`) |
| Disruption history | Credibility — real episodes (2011, 2020, chips) + demo analog flag |

---

### D.5 Parts catalog

| Element | Why |
|---------|-----|
| Category filter | Navigate 21+ parts |
| Criticality stars | Stockout impact |
| Supplier chips | Who serves this part |
| Risk badge | Post-run composite |
| **Why** button | Opens TOPSIS / allocation explainability |

---

### D.6 Suppliers

| Subtab | Why |
|--------|-----|
| Directory | Master data + Fear/Greed columns |
| Sourcing matrix | Part-centric allocation + mitigation playbooks |
| **↗ on name** | `reference_url` — public homepage (MRF, IndiaMART category) |

---

### D.7 Fear & Greed

| Element | Why |
|---------|-----|
| Hero gauge | OEM-level sentiment |
| Supplier table | Compare peers |
| Gauge grid | Visual scan |
| Bulletin cards | Narrative briefings (news, drivers, macro) |
| Knowledge panel | Full-screen explanation for presentations |

---

### D.8 Scenario lab

| View | Why |
|------|-----|
| Catalog | What-if library |
| Results table | Numbers for each strategy |
| Heatmap | Compare stockout % at a glance |

---

### D.9 AI & twin

| Subtab | Why |
|--------|-----|
| AI Hub | Future ML services catalog |
| Digital twin | Plant-level synthetic telemetry |

---

### D.10 Why panel (drawer)

**Why exists:** Professor / auditor asks “why this supplier?” — show **criteria table**, **ranks**, **allocation drivers**.

**Data:** `part_rankings`, `recommendations[].rationale`, `mcdm` detail rows.

---

### D.11 Chatbot

**Why:** Natural language for executives; must use **same snapshot** as UI.

**Extra:** `enrichment.py` fetches Google News + Yahoo Finance so answers are not hollow.

**Not:** A replacement for the pipeline — it **reads** pipeline output.

---

## Part E — “Run analysis” pipeline (story order)

```
1. INGEST     → World Bank, GDELT, RSS, (optional FRED)
2. CLASSIFY   → news_keywords.yaml → severity 1–5, country_code
3. RISK       → country, commodity, supplier scores (0–100)
4. MCDM       → TOPSIS rank per part
5. SIMULATE   → SimPy × 13 scenarios × 3 strategies × 30 runs
6. ALLOCATE   → recommendations + sourcing_matrix
7. ENRICH     → fear_greed, command_signals, tire_brief, ai_models, digital_twin, disruption_history
8. SAVE       → data/snapshots/latest.json + DuckDB
```

**If professor asks “is this real-time?”**  
Ingest pulls **live public APIs** when network works; scores are **recomputed** each run. Supplier/part master data is **YAML config**, not ERP.

---

## Part F — Config files (why each exists)

| File | Role in story |
|------|----------------|
| `suppliers.yaml` | Who is in the network; lead times; URLs |
| `parts.yaml` | What MSIL buys; criticality; alternates |
| `scenarios.yaml` | What shocks to simulate (Gulf tyre, chips, …) |
| `mcdm.yaml` | How to rank suppliers |
| `thresholds.yaml` | When to dual-source |
| `news_keywords.yaml` | How to score headlines |
| `data_sources.yaml` | Which countries & APIs to query |
| `maruti_company.yaml` | Company brief text |
| `strategic_analysis.yaml` | SWOT/PESTLE content |
| `supply_disruptions_history.yaml` | Timeline episodes |
| `ai_models.yaml` | Fake ML fleet metadata |
| `plants.yaml` | Digital twin nodes |

---

## Part G — Quick traceability table (number → origin)

| UI number | Origin function | Config / API |
|-----------|-----------------|--------------|
| Country risk 62.4 | `score_countries` | World Bank + news |
| Supplier risk 71.2 | `score_suppliers` | country + commodity + lead_time |
| Fear 58.3 | `_score_supplier_fear_greed` | weights in fear_greed.py |
| Greed 44.1 | same | cost_index, flags |
| TOPSIS rank 1 | `topsis_rank` | mcdm.yaml weights |
| Allocation 68/32 | `compute_part_allocation` | thresholds.yaml + sim stockout |
| Stockout P 100% | `run_scenarios` Monte Carlo | scenarios.yaml shock |
| News severity 4/5 | `classify_articles` | news_keywords.yaml |
| Twin OEE 78.2% | `_plant_metrics` hash | digital_twin.yaml plants |
| Part exposure % | `_supplier_part_weights` | parts criticality |

---

## Part H — Honest limitations (good to say proactively)

1. **Demo / educational** — not MSIL confidential data.  
2. **Fear & Greed** — heuristic indices, not market indices.  
3. **Simulation** — stylized SimPy, not digital twin calibration.  
4. **TOPSIS inputs** — mix of live macro/news and **hand-set** cost_index/lead times.  
5. **Chat** — can hallucinate if Ollama ignores context; enrichment helps but does not guarantee facts.  
6. **IndiaMART links** — category discovery, not supplier approval.

---

## Part I — Cheat sheet for common professor questions

| Question | Short answer |
|----------|--------------|
| What is **TH**? | Thailand (ISO country code). |
| What is **AE**? | United Arab Emirates — Gulf feedstock in demo. |
| What is **lead time**? | Days to get parts; longer → higher risk & fear. |
| How is **Fear %** calculated? | Weighted blend of supplier/country/commodity risk, lead time, news — see §B.2. |
| How is **Greed %** calculated? | Stability, cost index, low risks, EV/tier bonuses — §B.3. |
| Why **Run analysis**? | Rebuild snapshot so all widgets use same data. |
| Where do **suppliers** come from? | `config/suppliers.yaml` (35 demo archetypes). |
| Why **TOPSIS**? | Multi-criteria supplier ranking per part. |
| Why **SimPy**? | Show stockout probability under shocks. |
| Why **dual source**? | When risk or simulated stockout exceeds thresholds in `allocation.py`. |
| Is chat **ChatGPT**? | Local **Ollama**; context from our snapshot file. |

---

*Prepared for viva / project defense. Update this file if you change formulas in `fear_greed.py`, `risk.py`, or `allocation.py`.*
