<div align="center">

# 🏏 STRIKE//OS PRO
### Institutional Cricket Intelligence, Tactical Simulation & Grand League Analytics Workstation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2.8-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6.svg?style=flat&logo=TypeScript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF.svg?style=flat&logo=Vite&logoColor=white)](https://vitejs.dev)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5.6-FFF000.svg?style=flat&logo=DuckDB&logoColor=black)](https://duckdb.org)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT%20v9.10+-4285F4.svg?style=flat&logo=Google&logoColor=white)](https://developers.google.com/optimization)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.3-38B2AC.svg?style=flat&logo=Tailwind-CSS&logoColor=white)](https://tailwindcss.com)
[![Three.js](https://img.shields.io/badge/Three.js-0.186-black.svg?style=flat&logo=Three.js&logoColor=white)](https://threejs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  A production-grade, full-stack quantitative cricket platform combining <b>25 industry-standard analytics capabilities</b>, a <b>194,000+ delivery DuckDB columnar warehouse</b>, a <b>Hierarchical Bayesian shrinkage model</b>, <b>zero-leakage XGBoost projections</b>, and a <b>Google OR-Tools CP-SAT Grand League portfolio solver</b> across 12 reactive workspaces.
</p>

[Key Features](#-key-features) •
[Architecture](#-system-architecture) •
[12 Integrated Workspaces](#-12-integrated-workspaces) •
[Mathematical Engine](#-mathematical--analytical-foundations) •
[Quickstart](#-quickstart-guide) •
[API Reference](#-api-endpoints) •
[Configuration](#-configuration)

</div>

---

## 🌟 Key Features

- **⚡ Sub-10ms Columnar Analytics**: Powered by an embedded DuckDB columnar database indexing over **1,243 historical T20 matches** and **194,239+ ball-by-ball deliveries**.
- **🎯 Mathematical Grand League Optimizer**: Solves complex combinatorial lineups using **Google OR-Tools CP-SAT (Constraint Programming - Satisfiability)** with strict Cumulative Selection Percentage (CSP $500\%-650\%$), M-N-C partitioning, and Captain/Vice-Captain combinatorics.
- **🧠 Zero-Leakage XGBoost ML Predictor**: Gradient-boosted feature pipeline predicting mean fantasy points, 10th percentile floor, and 90th percentile ceiling scores without historical test leakage.
- **🔬 Hierarchical Bayesian Shrinkage**: Resolves small-sample Head-to-Head (H2H) duels using empirical Bayesian partial pooling against league-wide baselines.
- **🎮 Spatial 3D WebGL / Three.js Pitch Simulator**: Real-time 3D pitch perspective, bounce lengths, boundary radius geometry, and fielder coordinate mapping.
- **🌦️ DLS & Monte Carlo Rain Simulator**: Duckworth-Lewis-Stern resource calculation alongside 10 probabilistic match scenario scripts for weather interruptions.
- **📡 5-Hub Multi-Provider Telemetry**: Resilient data gateway with automatic fallback across Cricsheet (local), CricketData/CricAPI, Sportmonks, Roanuz Cricket, and Roanuz Fantasy APIs.
- **🖥️ 12 Dedicated Modular Workspaces**: A high-density tactical interface designed for elite analysts, coaches, and quantitative fantasy sports portfolio managers.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                              STRIKE//OS FRONTEND                                  |
|  React 19.2.8 | TypeScript 6.0 | Vite 8.3 | Tailwind CSS v4 | Three.js 0.186       |
|  12 Dedicated Workspaces • AppShell • MatchContext • Tactical Intelligence Drawer |
+-----------------------------------------------------------------------------------+
                                         │  HTTP / JSON (Port 8000)
                                         ▼
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND SERVICE                              |
|  Python 3.10+ | FastAPI 0.115+ | Uvicorn | Pydantic v2 | In-Memory State Caching  |
+-----------------------------------------------------------------------------------+
         │                                │                                │
         ▼                                ▼                                ▼
+--------------------+        +-----------------------+        +--------------------+
|   COLUMNAR WAREHOUSE|       |  OPTIMIZATION & ML    |        | MULTI-PROVIDER HUB |
| DuckDB v1.5+       |        | Google OR-Tools CP-SAT|        | Roanuz Cricket     |
| 1,243 T20 Matches  |        | XGBoost Regressor     |        | Roanuz Fantasy     |
| 194,239 Deliveries |        | Hierarchical Bayesian |        | Sportmonks v2.0    |
| Microsecond OLAP   |        | Monte Carlo Simulator |        | CricketData / Cric |
+--------------------+        +-----------------------+        | Cricsheet Archive  |
                                                               +--------------------+
```

---

## 💻 12 Integrated Workspaces

| # | Workspace ID | Core Component | Analytical Capability |
|:-:|:---|:---|:---|
| 1 | **`command-center`** | `CommandCenter.tsx` | Marquee match overview, toss decisions, weather & soil moisture, win probabilities, and live match cards. |
| 2 | **`game-plan`** | `GamePlan.tsx` | Over-by-over (1–20) tactical coach's board, bowler allocation, matchup rationale, and phase breakdown. |
| 3 | **`field-strategy`** | `FieldStrategy.tsx` | Interactive 2D/SVG field designer, Law 28 compliance validation, and 3D trap synchronizer. |
| 4 | **`pitch-lab`** | `PitchLab.tsx` | Hawk-Eye bounce lengths, boundary geometry, spatial 3D duel simulator, and pitch degradation tracking. |
| 5 | **`battle-arena`** | `BattleArena.tsx` | Micro batter vs bowler H2H matrix, delivery telemetry, and Bayesian shrinkage confidence indicators. |
| 6 | **`player-intel`** | `PlayerIntel.tsx` | 22-player comprehensive directory, XGBoost ML output, 90% credible intervals, and role filters. |
| 7 | **`ball-by-ball`** | `BallByBallLab.tsx` | Granular delivery log explorer, phase filters (Powerplay/Middle/Death), run-rate wagon wheel, and wicket markers. |
| 8 | **`scenario-lab`** | `ScenarioLab.tsx` | Duckworth-Lewis-Stern (DLS) rain calculator, interrupted overs simulations, and 10 Monte Carlo game scripts. |
| 9 | **`match-archive`** | `MatchArchive.tsx` | Multi-match bilateral series archive (Matches 1–4 scorecards + 5th decider tactical briefing). |
| 10 | **`fantasy-lab`** | `FantasyLab.tsx` | Google OR-Tools CP-SAT Grand League solver, M-N-C classification, CSP bounds ($500\%-650\%$), and 20-portfolio generation. |
| 11 | **`ai-analyst`** | `AIAnalyst.tsx` | Quantitative tactical chat assistant with pre-programmed institutional prompts and automated match intelligence dossiers. |
| 12 | **`settings-providers`**| `SettingsProviders.tsx` | Authentic 5-hub telemetry monitor, WebGL rendering quality toggles, and MCP tool status. |

---

## 📐 Mathematical & Analytical Foundations

### 1. Integer Linear Programming via Google OR-Tools CP-SAT
The fantasy portfolio optimizer formulates team selection as a multi-objective Constraint Satisfaction Problem (CSP):

$$\max \sum_{i \in \mathcal{P}} x_i \cdot \text{Proj}_i + 2 \cdot c_i \cdot \text{Proj}_i + 1.5 \cdot v_i \cdot \text{Proj}_i$$

Subject to strict institutional fantasy rules:
- **Squad Size**: $\sum_{i \in \mathcal{P}} x_i = 11$
- **Budget Constraint**: $\sum_{i \in \mathcal{P}} x_i \cdot \text{Credit}_i \le 100.0$
- **Team Composition**: $1 \le \sum_{i \in \text{Team}_A} x_i \le 10$ and $1 \le \sum_{i \in \text{Team}_B} x_i \le 10$
- **Role Distribution**:
  - Wicket-Keepers (WK): $1 \le \sum_{i \in \text{WK}} x_i \le 8$
  - Batters (BAT): $1 \le \sum_{i \in \text{BAT}} x_i \le 8$
  - All-Rounders (AR): $1 \le \sum_{i \in \text{AR}} x_i \le 8$
  - Bowlers (BOWL): $1 \le \sum_{i \in \text{BOWL}} x_i \le 8$
- **Cumulative Selection Percentage (CSP)**: $500\% \le \sum_{i \in \mathcal{P}} x_i \cdot \text{SelPct}_i \le 650\%$ (Grand League sweet-spot)
- **Captain & Vice-Captain**: $\sum_{i \in \mathcal{P}} c_i = 1, \quad \sum_{i \in \mathcal{P}} v_i = 1, \quad c_i + v_i \le x_i$

### 2. Empirical Bayesian Shrinkage for H2H Battles
To prevent sample-size distortion when a batter has faced a bowler for fewer than 20 balls:

$$\theta_{\text{shrunk}} = \frac{\tau^2}{\tau^2 + \sigma^2/n} \cdot \bar{y} + \frac{\sigma^2/n}{\tau^2 + \sigma^2/n} \cdot \mu_{\text{prior}}$$

Where $\mu_{\text{prior}}$ represents the batter's baseline against that bowler's bowling archetype (e.g., SLA, Off-Spin, Right-Arm Fast), and $n$ is the observed ball count.

### 3. DLS Interruption Resources
Resource loss percentage computed from the standard decile exponential decay curve:

$$R(u, w) = R_0(w) \cdot \left(1 - \exp\left(-\frac{b \cdot u}{R_0(w)}\right)\right)$$

Where $u$ represents remaining overs and $w$ represents lost wickets.

---

### 4. The 4 Universal Match Archetypes (The Game Script Framework)
To win institutional Grand Leagues (270k to 1M+ spots), the engine eliminates single-point average expectations ($E[P]$) and classifies any fixture into one of four game-state archetypes:

```
                                    CRICKET FIXTURE
                                           │
         ┌──────────────────┬──────────────┴──────────────┬──────────────────┐
         ▼                  ▼                             ▼                  ▼
    ARCHETYPE 1        ARCHETYPE 2                   ARCHETYPE 3        ARCHETYPE 4
   The Road / Flat   The Low-Scoring Minefield     The Powerhouse vs    The High-Stakes
   Highway (200+)      (120–140 Spin/Seam)          Underdog Mismatch    Parity Derby
```

1. **ARCHETYPE 1: Road / High-Scoring Highway (Par 195–230)**:
   - *Dynamics:* True bounce, minimal lateral movement, fast outfield.
   - *Lineup Rule:* Top-order stacking (Openers + No. 3 face ~70% of deliveries).
   - *Fade Rule:* Fade specialist powerplay-only bowlers (bleed runs, high economy penalties).
   - *Captaincy Rule:* Top-3 Batters or Death Power Hitters (70+ milestone bonuses).

2. **ARCHETYPE 2: Minefield / Spin Choke (Par 125–145)**:
   - *Dynamics:* Gripping surface, variable bounce, sharp spin.
   - *Lineup Rule:* Stack 5 to 6 Bowlers/All-Rounders (bowlers outscore batters 2:1).
   - *Fade Rule:* Fade aggressive boundary-reliant openers (>60% bust rate).
   - *Captaincy Rule:* Mystery spinners and change-of-pace seamers (3 wkts + maiden = 110–135 pts).

3. **ARCHETYPE 3: Asymmetric Mismatch / Bilateral Dead-Rubber**:
   - *Dynamics:* Heavy favorite vs Associate/underdog (e.g. IND-W vs ZIM-W, AUS vs SCO).
   - *Underdog Law:* Opposition 2-way all-rounders bowling death overs + batting top 4 are guaranteed maximum volume.
   - *Captaincy Rule:* Leverage middle-order accelerations and underdog all-rounder VC.

4. **ARCHETYPE 4: High-Stakes Parity Derby (Even Strength)**:
   - *Dynamics:* High tactical preparation, narrow victory margins (IND vs PAK, IPL playoffs).
   - *Lineup Rule:* 6-5 split; micro-matchup exploitation (e.g. SLA vs RHB top-order vulnerability).

---

### 5. The 3 Invariable Laws of Rank 1 Lineup Generation

$$\text{Leverage } L_i = z(E[P_i]) - z(\text{own}_i) \quad \Big| \quad P(\text{Cap}) \times P(\text{VC}) \le 0.05$$

* **Law I: The Unspent Credit Structural Shield ($81.0 - 86.5$ Credits Spent)**:
  Over 92% of the casual public forces expensive players to reach 99.0–100.0 credits. Leaving **13.5 to 19.0 credits unspent** guarantees **zero to sub-2 duplicate teams** across a 270,000-entry contest while preserving maximum 95th-percentile ceiling points.

* **Law II: C/VC Ownership Independence ($P(\text{Cap}) \times P(\text{VC}) \le 0.05$)**:
  Combined ownership product of Captain and Vice-Captain must not exceed 5%. Unlocks sole ownership of Rank 1 without requiring 11 low-floor differential punts.

* **Law III: Game Script Coherence (Positive Covariance)**:
  Eliminates internal cannibalization. Every player in the 11 must make sense within the same 40-over narrative (e.g., favorite strike bowlers paired with underdog middle-order all-rounders, not dismissed openers).

---

### 6. Dead-Rubber Captaincy Bias Filter & The "Two Bites at the Cherry" Rule

* **Dead-Rubber Captaincy Filter**:
  When a series is decided (2-0 up) and a captain explicitly announces *"giving game time to the middle order"*, apply a **-35% balls-faced projection penalty to the captain** and boost middle-order No. 3–5 batters by **+35% to +45%**.
* **The "Two Bites at the Cherry" Law**:
  In asymmetric mismatches, an underdog all-rounder who bowls death overs (4 overs) AND bats in the top 4 has two independent Poisson processes generating fantasy points. In GPPs, this player carries a higher 95th-percentile ceiling than a specialist bowler and should be prioritized for **Vice-Captaincy**.

---

### 7. Forensic Case Study: India Women vs Zimbabwe Women (3rd T20I, Raipur)

| Metric | User T1 | Winning Team (JOY MA TARA \| T8) | Tactical Driver |
| :--- | :---: | :---: | :--- |
| **Total Score** | 1,031.5 pts | **1,309.0 pts** (+277.5) | **Rank 1 Overall Champion** |
| **Captain (2.0x)** | H. Kaur (366 pts) | H. Kaur (366 pts) | 91* off 41 balls (21% owned leverage) |
| **Vice-Captain (1.5x)**| K. Gaud (67.5 pts) | **B. Biza (252.0 pts)** | 3 wkts + 44 runs (Two Bites at the Cherry) |
| **Star Batter Fade** | S. Mandhana (4 pts) | **S. Mayers (112.0 pts)** | Mandhana DNB; Mayers scored 60 off 49 |
| **Underdog All-Rounder**| J. Nkomo (4 pts - DNB) | **N. Gwanzura (57.0 pts)** | Gwanzura 1 wkt + 2 catches |
| **Credits Unspent** | 15.0 Cr Unspent | **15.0 Cr Unspent** | Absolute zero duplicates in 270k field |

---

## 📡 Provider Integrations (`gl_engine/providers/data_hub.py`)

| Provider | Status | Best Use Case | Auth Requirement |
|---|---|---|---|
| **Cricsheet & DuckDB** | `LOCAL_ARCHIVE_READY` (< 1ms) | Historical ball-by-ball match data, empirical backtesting | Open-source local archive (`t20.duckdb` & `data/cricsheet_wt20.duckdb`) |
| **CricketData / CricAPI** | `AUTHENTICATED_LIVE` / `STANDBY` | Live match discovery & confirmed squad verification | API Key (`CRICKETDATA_API_KEY`) |
| **Sportmonks Cricket API** | `AUTHENTICATED_LIVE` / `STANDBY` | Comprehensive scorecards, playing XI lineups, bowling figures | API Token (`SPORTMONKS_API_TOKEN`) |
| **Roanuz Cricket API** | `AUTHENTICATED_LIVE` / `STANDBY` | Real-time live match intelligence, micro-events, and toss tracking | Project & App Key (`ROANUZ_API_KEY`) |
| **Roanuz Fantasy API** | `AUTHENTICATED_LIVE` / `STANDBY` | Real-time official fantasy scoring & player credit values | Project & App Key (`ROANUZ_API_KEY`) |

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **Node.js** (Optional, for frontend development): Node 18+ and npm 9+
- **Git**

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/Tashima-Tarsh/Cricket.git
cd Cricket
```

### Step 2: Set Up Python Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Variables (Optional)
Copy `.env.example` to `.env` and fill in API keys if live polling is required:
```bash
cp .env.example .env
```
*(The platform operates seamlessly offline using DuckDB and pre-compiled historical intelligence even without external API keys).*

---

### Step 5: Run the Server
Launch the unified server (FastAPI serves both backend API and pre-compiled React frontend on port 8000):
```bash
python run_server.py
```
*Or via Uvicorn directly:*
```bash
python -m uvicorn gl_engine.web_app:app --host 127.0.0.1 --port 8000
```

Open your browser at **[http://localhost:8000](http://localhost:8000)**.

---

### 🛠️ Frontend Development (Optional)
If you wish to modify or build the React 19 / Vite UI:
```bash
cd frontend
npm install
npm run dev      # Starts Vite dev server with hot-reload at http://localhost:5173
npm run build    # Compiles assets into frontend/dist/
```

---

## 🔌 API Endpoints

The FastAPI backend exposes comprehensive REST endpoints for analytics and programmatic consumption:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check, DuckDB connection status, and model versions |
| `GET` | `/api/state` | Full cached tactical intelligence state (sub-10ms response) |
| `POST` | `/api/optimize` | Solves CP-SAT Grand League lineups with custom constraints |
| `GET` | `/api/cricsheet/duckdb-stats` | Columnar database summary (deliveries, matches, teams) |
| `GET` | `/api/cricsheet/matches` | Historical match explorer with innings breakdowns |
| `POST` | `/api/scenario/simulate` | Executes DLS and interrupted overs simulations |
| `GET` | `/api/backtesting/replays` | Historical match delivery replays for model evaluation |
| `GET` | `/api/providers/status` | Real-time connectivity telemetry for all 5 data providers |

Interactive Swagger documentation is available at **`http://localhost:8000/docs`**.

---

## 📂 Project Structure

```
Cricket/
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── pyproject.toml                  # Python package configuration
├── requirements.txt                # Python dependencies
├── README.md                       # Repository documentation
├── run_server.py                   # Server launcher
├── start_server.bat                # Windows 1-click batch launcher
├── t20.duckdb                      # DuckDB warehouse (1,243 matches, 194,239 deliveries)
│
├── gl_engine/                      # Core Intelligence Engine
│   ├── web_app.py                  # FastAPI server & route handlers
│   ├── ortools_optimizer.py        # Google OR-Tools CP-SAT portfolio generator
│   ├── xgboost_model.py            # Zero-leakage XGBoost projection engine
│   ├── bayesian_shrinkage.py       # Empirical Bayesian H2H smoothing
│   ├── cricsheet.py                # Cricsheet parser & ingestion engine
│   ├── rain_model.py               # Duckworth-Lewis-Stern (DLS) calculator
│   ├── match_catalog.py            # Match catalogs and fixtures
│   ├── player_resolver.py          # Cross-platform player name entity resolution
│   ├── wt20_analytics.py           # WT20 analytical registry
│   └── providers/                  # Multi-provider integrations (Roanuz, Sportmonks, CricAPI)
│
├── frontend/                       # React 19 Frontend Application
│   ├── src/
│   │   ├── components/             # 12 Workspace components (CommandCenter, FantasyLab, etc.)
│   │   ├── context/                # MatchContext & global state providers
│   │   └── services/               # API clients & telemetry hooks
│   ├── dist/                       # Production pre-built web assets (served by FastAPI)
│   ├── package.json                # Frontend dependencies
│   └── vite.config.ts              # Vite 8 configuration
│
├── data/                           # Data storage & DuckDB archives
│   ├── cricsheet_wt20.duckdb       # Women's T20 DuckDB database
│   ├── indw_zimw_raw_roster.json   # Verified roster schema
│   └── cricsheet/                  # Raw Cricsheet match archives
│
├── docs/                           # Architectural blueprints & dossiers
│   ├── MASTER_MATCH_INTELLIGENCE_DOSSIER.md
│   ├── STRIKE_OS_AUDIT.md
│   └── UI_FRONTEND_FIXES.md
│
└── tests/                          # Automated test suites
    └── test_workspace_api.py
```

---

## 🧪 Testing

Run backend tests using Python:
```bash
python -m pytest tests/
```
Or run component verification:
```bash
python test_app.py
python test_all_components.py
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <b>Built for quantitative cricket analysts, tactical strategists, and performance researchers.</b>
</div>
