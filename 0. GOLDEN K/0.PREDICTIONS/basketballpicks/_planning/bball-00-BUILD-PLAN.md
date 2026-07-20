# basketballpicks — Consolidated Build Plan

*Synthesis of five parallel design agents (scaffold · leagues · core model · props edge · odds+validation), 2026-07-19. Grounded in `basketball-feasibility.txt` and the safepicks `profitability-verdict-2026-07` verdict.*

---

## 0. The honest verdict (read this first)

basketballpicks is **buildable, fast, and cheap** (4–8 week MVP, reuses ~60% of the safepicks Django/Postgres stack, one mandatory spend). But be clear-eyed about what it *is*:

- **The main market (spread/ML/total) is as dead as soccer.** A points model goes **market-GRADE, not market-beating** — it stalls at the same information ceiling (lineups, minutes, injury-timing, sharp flow). We do NOT build a main-market betting system.
- **The one live edge is player props / DFS pick'em — and ~90% of it is devig + line-shopping arbitrage, not model superiority.** OddsJam/Outlier already sell that engine. Our model earns its keep *only* in the neglected corners: WNBA, college, rare stats (blocks/steals/deep-bench), and the injury-minute cascade.
- **The edge is real but capped and declining** (~+2–6% ROI/entry, high variance, low-4-to-low-5 figs/yr solo), taxed by soft-book limiting and eroding as DFS pivots to peer-to-peer (Underdog Arena / PrizePicks Champions, a real 2026 shift toward pure rake).
- **The product is therefore two honest things:** (1) a market-grade multi-league predictor, and (2) a props/DFS line-shop engine that lives or dies by a **pre-registered forward-CLV gate** — the discipline soccer lacked.

If the forward-CLV gate confirms → scale carefully. If it kills → keep the honest predictor, drop the betting claim. Either way we get a clean answer in ~8 weeks of paper capture.

---

## 1. Architecture (agent 01)

Mirror safepicks; **player-first schema** is the key departure. ~12 Django apps:

- `core` — **adds** Player, Game, TeamBoxScore, **PlayerBoxScore** (minutes/usage grain — the differentiator), PlayByPlay (optional)
- `ingestion` — JobRun + ETL orchestrator + nba_api/odds sources
- `features` — TeamRating + **PlayerForm / MinutesProjection**
- `odds` — team markets + **shared Shin devig** + `sharp_anchor`
- **`props`** (new hero data app) — PropMarket, **PropLine** (two-sided O/U per player-market-book, DFS-aware), **PropConsensus** (devigged sharp-fair benchmark), PropPrediction
- **`edge`** (hero publisher) — EdgeRule, **EdgePick** (devig-centric, model optional), ProductionModel, PipelineState
- `predictions` (team, market-grade, de-emphasised), `secondary`, `backtesting`, `portfolio` (Bet + **DFSEntry**), `dashboard`, `api`

**Copy-verbatim from safepicks:** devig, BudgetedClient HTTP, JobRun, ramp/cadence/notifications, engine base + calibrators, Bankroll/Bet, Docker/CI.
**Build fresh:** the entire `props` app, Player/box-score models + nba_api parser, minutes/Poisson engines, DFSEntry correlation math.

---

## 2. Leagues & data (agent 02)

**35 leagues** enumerated. **MVP set = NBA + WNBA + NCAA Men's D1 + EuroLeague.** Start even tighter (NBA + WNBA) to prove the devig engine before DFS-scrape complexity.

**Best free player-level sources:**
1. **nba_api** — richest anywhere (player box + full PBP + tracking + minutes/usage, no key)
2. **hoopR / wehoop** (via sportsdataverse) — NCAA M/W D1 + WNBA player box + PBP
3. **euroleague-api** — EuroLeague + EuroCup box/PBP/shots

**Load-bearing constraints:**
- The Odds API sells sportsbook **player props for NBA + WNBA only.** All other leagues' prop edge = **DFS pick'em scraping** (no clean API).
- **Prop history starts 2023-05-03** → validate **forward**, deep backtest impossible.
- **API-Basketball** (free 100/day) unlocks ~20 international leagues in Phase 2 (player-box depth "verify" below top-Europe).

---

## 3. Core model (agent 03)

**Retire Dixon-Coles.** A game ≈ 100 near-independent possessions → by CLT the **margin is ~Gaussian.** Model *Points = Possessions × Points-Per-Possession* with opponent-adjusted efficiency ratings (ridge-adjusted efficiency v1; margin-Elo cold-start/ensemble; RAPM frontier), home court, rest/B2B/3-in-4, travel → a **Normal/skew-t distribution over MARGIN and TOTAL** (σ≈11–13 pts, widening under lineup uncertainty). Spread/ML/team-total/total all derive from one distribution.

**Player-prop model (the differentiator):** hierarchical — **minutes distribution** (dominant uncertainty) → usage × pace → per-stat distributions (compound Binomial points; Neg-Binomial reb/ast/3PM; copula-summed PRA/combos). Natively **re-solves the lineup on injury** (a starter's minutes/usage flow to specific teammates).

**Calibratable (market-grade):** spread/ML/total, team totals, **rebounds (best target)**, points, PRA, lead-guard assists.
**Noise — devig-or-display only, never our own edge (the cards/BTTS analog):** blocks, steals, threes-made, first-basket, exact-stat/race-to-N novelties, thin quarter/half sub-markets.

Calibration-gated (isotonic/beta by band-ECE/bias; PIT/CRPS for distributions), champion/challenger promotion, walk-forward with sealed pre-closing holdout, **validated forward via paper-CLV.**

---

## 4. The edge engine (agent 04)

De-vig the sharp consensus (Pinnacle/Circa) → true per-player stat **distribution** → reprice that fitted CDF at each soft-book and DFS line → bet only where their stale number beats the true side past their (large) hold. Unlike 1X2 you must **reprice a CDF, not compare prices** (venues quote the same player at *different lines*).

- **DFS pick'em hold is brutal** (25–61%): a 2-pick needs **57.7%/leg**, a 3-pick **55.0%** — only whole-point line errors pushing true prob ≥60% clear it.
- **Biggest EV lever is correlation, not the model:** a +0.9% line-only 2-leg becomes **+15% at ρ=0.2** on same-game stacks — also the noisiest, most-policed input.
- **Model matters only where sharps don't price** (WNBA/college/rare stats/deep-bench/injury cascades) as a higher-threshold, **half-stake fallback anchor**. Against a well-quoted sharp line it cannot win.

---

## 5. Odds ingestion · settlement · validation (agent 05)

**Ingestion:** The Odds API **Business tier ($99/mo — the only tier with props + Pinnacle + history).** Team markets on bulk `/odds`; props on per-event `/events/{id}/odds` (free `/events` enumerates game IDs at zero cost first). DFS lines from **PrizePicks/Underdog** reverse-engineered JSON (or Apify actors), stored price-less. **Intraday cadence:** open sweep → hourly → **critical 10-min sweeps inside T-90min** (the injury-bulletin cascade) → closing flag; BudgetedClient reserves credits for the final window.

**Settlement:** nba_api box scores → PlayerBoxScore; one grader maps stat-vs-line for every prop + final score, with pre-committed edge cases (DNP/0-min → VOID, exact-line → push, two-way Porter-rule under-void, OT included, 48h idempotent re-grade for stat corrections).

**Forward-CLV gate (`prop_clv.py`):** flag every soft/DFS line the Shin-de-vigged anchor prices +EV, then at lock measure three CLV flavors — same-book price CLV, line-move CLV (price-less DFS), and the verdict metric **sharp-beat CLV** (taken price vs sharp's closing fair). Aggregate per market/book/league with bootstrap 95% CIs vs **frozen pre-registered thresholds:**
- **CONFIRM:** n≥500, mean sharp-beat CLV ≥+2%, CI lower bound >0, sustained ≥8 weeks
- **KILL:** n≥300 with CLV≤0, or ROI CI upper bound <0
- **Every cell starts DISABLED; moving a threshold requires a dated ADR.**

---

## 6. Phased roadmap

| Phase | What | Cost | Weeks |
|---|---|---|---|
| **0 — Scaffold** | Stand up Django+Postgres+Docker, 12 apps, copy-verbatim infra, player-first schema. No data. | free | 1 |
| **1 — MVP harvest** | nba_api (NBA) + wehoop (WNBA) first; then hoopR (NCAA-M) + euroleague-api. Team + player box + schedules. | free | 1–2 |
| **2 — Core model** | pace×efficiency team model + hierarchical player-prop model; calibrate; walk-forward vs closing line. | free | 2–4 |
| **3 — Edge engine** | Odds API Business live; port sharp_anchor → prop devig/CDF reprice; DFS math; flag +EV. | **$99/mo** | 3–5 |
| **4 — Forward-CLV gate** | prop_clv.py + 3 CLV flavors + pre-registered thresholds; 500-leg / 8-week paper mini-run. **Decides everything.** | — | 4–8+ |
| **5 — Expand / decide** | CONFIRM → API-Basketball unlocks ~20 intl leagues, scale stakes, rotate venues. KILL → keep honest predictor. | staged | post |

**Total mandatory spend to reach a verdict: $99/mo (Odds API Business), and only from Phase 3.** Phases 0–2 are entirely free.

---

## 7. Guardrails carried over from soccer
- Never lower a CLV threshold to keep a dying edge breathing — kill it.
- Paper-only until the gate confirms; no real money on an unvalidated edge.
- Honesty banners on every high-variance surface (as on safepicks /high-odds).
- The predictor product stands on its own even if the betting edge dies.
