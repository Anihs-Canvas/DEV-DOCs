# basketballpicks

A player-props / DFS pick'em **line-shop + validation** platform for basketball
(NBA · WNBA · NCAA-M · EuroLeague). Mirrors the safepicks Django/Postgres/Celery
stack, but the schema is **player-first** and the hero engine is **devig +
line-shop**, not a forecasting model.

> **The honest verdict** (`_planning/bball-00-BUILD-PLAN.md`): the main market
> (spread/ML/total) is as efficient as soccer's — a points model goes
> market-*grade*, not market-*beating*. The one live edge is player props / DFS,
> and ~90% of that is devig + line-shopping, not model superiority. So the
> product is two honest things: (1) a market-grade multi-league predictor, and
> (2) a props/DFS line-shop engine that lives or dies by a **pre-registered
> forward-CLV gate**. Paper-only until the gate confirms.

## Quickstart

```bash
cp .env.example .env          # keys optional — the pipeline no-ops politely without them
docker compose up             # web (migrate + gunicorn), worker, beat, postgres16, redis7
```

Bare local dev (no services) falls back to SQLite, so the test suite runs with
zero containers:

```bash
pip install -r requirements-dev.txt
python manage.py migrate      # the orchestrator makes migrations at integration time
pytest
```

## App layout (`config/settings.py` INSTALLED_APPS)

| app | role |
|---|---|
| **core** | reference + results; **Player + box scores** (the differentiator) |
| **ingestion** | JobRun audit, source-refs, **ETL orchestrator** (`etl.py`), `http.py` BudgetedClient, `sources/` |
| features | TeamRating(+pace) + PlayerForm + MinutesProjection |
| odds | TEAM markets (spread/ML/total) + shared Shin devig + sharp_anchor |
| **props** | HERO DATA APP — PropMarket / PropLine / PropConsensus (the differentiator) |
| predictions | ModelVersion / Prediction (team, market-grade) + PropPrediction |
| **edge** | HERO PUBLISHER — EdgeRule / EdgePick / ProductionModel / PipelineState |
| secondary | secondary-module flag registry |
| backtesting | settle / pnl / CLV; forward paper-CLV emphasis |
| portfolio | Bankroll / Bet (singles) + DFSEntry (pick'em parlays) |
| dashboard | read-only ops templates |
| api | DRF v1 read surface |

## The shared contract — `apps.core.models`

Everything else imports the canonical entities from here (never redefine them):

```python
from apps.core.models import League, Team, Player, Game, TeamBoxScore, PlayerBoxScore
```

`PlayerBoxScore` (minutes / usage grain) is the whole reason the project exists;
combos (PRA / PR / PA / RA / double-double) are **derived at settle time**, never
stored. See `_planning/bball-01-architecture-scaffold.txt` §2 for the full schema.

## The daily ETL

`apps/ingestion/etl.py` orchestrates one parent `JobRun` (`etl:daily`) over four
stages — **anchor → props → enrich → validate** — under the safepicks
no-key-no-crash / no-data-no-crash contracts (ADR 007). The blocking
data-quality gate (`validation.py`) vetoes a run with a non-zero exit rather than
let corrupt data reach publication. Source clients plug into `sources/`.

## Ops notes

- Everything UTC. Money/odds/minutes are `DecimalField`. Verbatim source rows are
  kept in `raw` JSON for re-parsing.
- Celery queues are split `core` / `ingestion` / `secondary` so slow keyless
  nba_api pulls never delay the T-90m prop loop.
- Design docs live in `_planning/`. The soccer sibling `../safepicks` is the
  read-only pattern reference.
