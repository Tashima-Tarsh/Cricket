# 🏏 Fantasy Cricket Grand League Engine

Automated fantasy cricket engine that ingests real ball-by-ball data from Cricsheet,
engineers per-player fantasy features, trains LightGBM mean + variance models with an
automated versioned pipeline, and generates Grand League lineups via OR-Tools CP-SAT.

## Features

1. **Data ingestion** (`cricsheet_loader.py`)
   - Downloads real ball-by-ball CSV ZIPs from https://cricsheet.org/
   - Local caching with 24h freshness; synthetic fallback when offline
2. **Feature engineering** (`feature_engineer.py`)
   - Converts ball-by-ball records into per-player match stats
   - Computes skill_rating, recent_form_last_5, opposition_strength,
     phase_strike_rate, economy_rate, and fantasy_points (target)
   - Dream11-style scoring with milestone bonuses
3. **Prediction** (`predictor.py`)
   - LightGBM dual-head regressor: expected points + variance (upside)
4. **Automated training pipeline** (`model_pipeline.py`)
   - Versioned model registry (`models/v1.0/`, `models/latest/`)
   - Metrics logging (`metrics.jsonl`)
   - Retrain decision heuristic
5. **Optimization** (`optimizer.py`)
   - OR-Tools CP-SAT Grand League optimizer
   - Hard constraints: 11 players, 100 credits, role bounds, max 7/team
   - Grand League constraints: anti-chalk, captain variance, scenario forcing
6. **Orchestration** (`main.py`)
   - End-to-end automated pipeline

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Explicit DEMO ONLY (contains historical/synthetic fallback and sample rosters)
CRICKET_DEMO_MODE=1 python main.py

# Synthetic data only (offline / no network)
python -c "
from main import run_pipeline
run_pipeline(use_cricsheet=False)
"
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Project Structure

```
fantasy_cricket_engine/
├── requirements.txt        # Python dependencies
├── data_loader.py          # Synthetic data + upcoming 22-player roster
├── cricsheet_loader.py     # Real Cricsheet ball-by-ball downloader/parser
├── feature_engineer.py     # Ball-by-ball -> fantasy features
├── predictor.py            # LightGBM mean + variance predictor
├── model_pipeline.py       # Automated training + versioned registry
├── optimizer.py            # OR-Tools CP-SAT Grand League optimizer
├── main.py                 # Automated pipeline orchestrator
├── README.md               # This file
├── models/                 # Versioned model artifacts (generated)
└── tests/
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_feature_engineer.py
    ├── test_predictor.py
    ├── test_optimizer.py
    └── test_pipeline.py
```

## Production Upgrade

- Replace `load_upcoming_match_players()` with a live scraper for Dream11/My11Circle selection%
  30 minutes before deadline
- Schedule `main.py` daily via cron / Airflow / GitHub Actions to retrain on new Cricsheet data
- Add a Flask/FastAPI API around `predictor.predict()` + `optimizer.optimize()` for team generation


## Free-only WBBL n8n integration (development)

See [Free WBBL n8n setup](docs/FREE_WBBL_N8N.md). The new implementation
accepts browser-visible Dream11 player data and WBBL match observations
without paid API keys. It fails closed on incomplete playing-XI evidence;
**this is not yet a certified autonomous post-toss fantasy system**.
