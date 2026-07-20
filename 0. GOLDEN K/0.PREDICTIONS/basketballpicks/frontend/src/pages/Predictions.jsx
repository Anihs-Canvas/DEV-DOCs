// Page 1 — Today's predictions. The team CORE model publishes a Gaussian
// margin/total distribution; from it we derive the moneyline, spread cover,
// and total over/under probabilities (prob_vector.ML / SPREAD / TOTAL). Shown
// alongside nothing but the model's own read — these are calibrated forecasts,
// not tips, and the market is efficient. Player projections carry the honest
// calibrate-vs-noise flag. Zero games is a designed state, never a blank page.
import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { fetchPredictionsToday } from "../api.js";
import {
  CalibrationChip,
  ErrorBox,
  Loading,
  PaperBanner,
  Tiles,
  useApi,
} from "../components.jsx";
import { dayLabel, dec, int, pct, signed, tipoffTime } from "../format.js";

const todayIso = () => new Date().toISOString().slice(0, 10);

function shiftDays(iso, delta) {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + delta);
  return d.toISOString().slice(0, 10);
}

// The date control mirrors safepicks' anchor bar: the selected day lives in the
// URL (?date=YYYY-MM-DD) so it persists and is shareable; empty = today.
function DateControl({ date }) {
  const [params, setParams] = useSearchParams();
  const shown = date ?? todayIso();
  const setDate = (value) => {
    const next = new URLSearchParams(params);
    if (!value || value === todayIso()) next.delete("date");
    else next.set("date", value);
    setParams(next, { replace: true });
  };
  return (
    <div className="anchor-bar" role="group" aria-label="Prediction date">
      <button className="anchor-btn" onClick={() => setDate(shiftDays(shown, -1))} title="previous day">
        ←
      </button>
      <input
        className="anchor-input"
        type="date"
        value={shown}
        onChange={(e) => setDate(e.target.value)}
        aria-label="Date"
      />
      <button className="anchor-btn" onClick={() => setDate(shiftDays(shown, 1))} title="next day">
        →
      </button>
      <button className={`anchor-btn ${date ? "" : "on"}`} onClick={() => setDate(null)} title="today">
        Today
      </button>
    </div>
  );
}

// A stacked model-market cell: the headline number over a subtle qualifier.
function ModelCell({ headline, sub }) {
  if (headline == null) {
    return (
      <td className="mkt">
        <span className="subtle">—</span>
      </td>
    );
  }
  return (
    <td className="mkt">
      <span className="mkt-main">{headline}</span>
      {sub ? <span className="mkt-sub subtle">{sub}</span> : null}
    </td>
  );
}

// Moneyline: from prob_vector.ML {HOME, AWAY}. Reports the model favourite.
function moneyline(pv) {
  const ml = pv?.ML;
  if (!ml || (ml.HOME == null && ml.AWAY == null)) return { headline: null };
  const home = ml.HOME;
  const away = ml.AWAY;
  const homeFav = (home ?? 0) >= (away ?? 0);
  return {
    headline: `${homeFav ? "HOME" : "AWAY"} ${pct(homeFav ? home : away)}`,
    sub: `home ${pct(home)} · away ${pct(away)}`,
  };
}

// Spread: prob_vector.SPREAD {line (home spread), HOME (cover prob)}.
function spread(pv) {
  const sp = pv?.SPREAD;
  if (!sp || sp.line == null) return { headline: null };
  return {
    headline: `HOME ${signed(sp.line)}`,
    sub: sp.HOME != null ? `cover ${pct(sp.HOME)}` : null,
  };
}

// Total: prob_vector.TOTAL {line, OVER, UNDER}.
function total(pv) {
  const t = pv?.TOTAL;
  if (!t || t.line == null) return { headline: null };
  const overFav = (t.OVER ?? 0) >= (t.UNDER ?? 0);
  return {
    headline: `${dec(t.line, 1)}`,
    sub: t.OVER != null ? `${overFav ? "over" : "under"} ${pct(overFav ? t.OVER : t.UNDER)}` : null,
  };
}

export default function Predictions() {
  const [params] = useSearchParams();
  const date = params.get("date"); // null = today (resolved server-side)
  const state = useApi(() => fetchPredictionsToday(date), [date]);

  const propsByGame = useMemo(() => {
    const map = {};
    (state.data?.prop_predictions ?? []).forEach((p) => {
      (map[p.game_id] = map[p.game_id] || []).push(p);
    });
    return map;
  }, [state.data]);

  if (state.loading) return <Loading what="today's predictions" />;
  if (state.error) return <ErrorBox error={state.error} what="predictions" />;

  const data = state.data ?? {};
  const team = data.team_predictions ?? [];
  const props = data.prop_predictions ?? [];
  const nGames = data.n_games ?? 0;

  return (
    <>
      <h1 className="page-title">Today's predictions</h1>
      <p className="page-sub">
        The CORE model's calibrated margin/total distribution for {dayLabel(data.date)} — from it
        we price the moneyline, spread cover, and total over/under. These are model forecasts shown
        for context; the market is efficient and nothing here is a tip.
      </p>
      <PaperBanner text="Model output only — displayed for research. No selection here is a bet." />
      <DateControl date={date} />

      <Tiles
        items={[
          { k: "Games", v: int(nGames) },
          { k: "Team predictions", v: int(team.length) },
          { k: "Player projections", v: int(props.length) },
          { k: "Date", v: dayLabel(data.date) },
        ]}
      />

      {nGames === 0 ? (
        <div className="card zero">
          <strong>No games tip off on {dayLabel(data.date)} — this is a designed state.</strong>
          <div className="label">
            Only calendar days with stored fixtures render rows. Nothing is fabricated to fill an
            empty slate.
          </div>
        </div>
      ) : null}

      {team.length ? (
        <section>
          <h2>Model team markets</h2>
          <p className="page-sub">
            Derived from each game's stored distribution (prob_vector). Spread line is the home
            side; cover / over probabilities are the model's, not a market quote.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Match</th>
                  <th>League</th>
                  <th>Tip-off</th>
                  <th>Moneyline (model)</th>
                  <th>Spread (model)</th>
                  <th>Total (model)</th>
                  <th>Model</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {team.map((row) => {
                  const pv = row.prob_vector || {};
                  const ml = moneyline(pv);
                  const sp = spread(pv);
                  const tot = total(pv);
                  const nProps = (propsByGame[row.game_id] ?? []).length;
                  return (
                    <tr key={row.game_id}>
                      <td>
                        <span className="fixture">{row.fixture ?? `game ${row.game_id}`}</span>
                      </td>
                      <td className="subtle">{row.league ?? "—"}</td>
                      <td className="subtle">{tipoffTime(row.tipoff_utc)}</td>
                      <ModelCell headline={ml.headline} sub={ml.sub} />
                      <ModelCell headline={sp.headline} sub={sp.sub} />
                      <ModelCell headline={tot.headline} sub={tot.sub} />
                      <td className="subtle">{row.model_version ?? "—"}</td>
                      <td>
                        <Link className="row-link" to={`/game/${row.game_id}`}>
                          detail{nProps ? ` · ${nProps} props` : ""} →
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {props.length ? (
        <section>
          <h2>Player projections</h2>
          <p className="page-sub">
            Minutes-driven per-stat projections. The calibration flag is the honest one: a{" "}
            <span className="chip warn">devig-only</span> market is a noise market — stored for
            display, never trusted as our own edge.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Market</th>
                  <th className="num">Proj min</th>
                  <th className="num">Proj mean</th>
                  <th>Dist</th>
                  <th>Calibration</th>
                  <th>Model</th>
                </tr>
              </thead>
              <tbody>
                {props.map((p, i) => (
                  <tr key={`${p.game_id}-${p.player}-${p.market_key}-${i}`}>
                    <td className="fixture">{p.player ?? "—"}</td>
                    <td>
                      <span className="chip info">{p.market_key ?? "—"}</span>
                    </td>
                    <td className="num">{dec(p.proj_minutes, 1)}</td>
                    <td className="num">{dec(p.mean, 2)}</td>
                    <td className="subtle">{p.dist ?? "—"}</td>
                    <td>
                      <CalibrationChip gate={p.calibration_gate} />
                    </td>
                    <td className="subtle">{p.model_version ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </>
  );
}
