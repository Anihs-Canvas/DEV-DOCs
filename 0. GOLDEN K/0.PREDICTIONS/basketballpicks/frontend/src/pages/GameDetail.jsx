// Page 4 — one game's detail: the full CORE prediction (every market the
// stored distribution prices, plus the raw margin/total params) and the player
// prop board (model projections beside book lines and the devig consensus
// fair). All null-safe: a game may have no stored prediction, no props, no
// consensus — each renders its own honest empty state, never a crash.
import { Link, useParams } from "react-router-dom";
import { fetchGamePrediction, fetchGameProps } from "../api.js";
import {
  CalibrationChip,
  ErrorBox,
  GameStatusChip,
  Loading,
  PaperBanner,
  Tiles,
  useApi,
} from "../components.jsx";
import { dec, odds, pct, signed, tipoffFull, tipoffTime } from "../format.js";

// A small labelled market card (moneyline / spread / total / team totals).
function MarketCard({ title, children }) {
  return (
    <div className="card market-card">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function Line({ k, v, tone }) {
  return (
    <div className="kv">
      <span className="kv-k">{k}</span>
      <span className={`kv-v ${tone ?? ""}`}>{v}</span>
    </div>
  );
}

function PredictionBlock({ prediction }) {
  if (!prediction) {
    return (
      <div className="card zero">
        <strong>No stored CORE prediction for this game.</strong>
        <div className="label">
          The game exists but no model row has been written for it yet — shown honestly rather than
          fabricated.
        </div>
      </div>
    );
  }
  const pv = prediction.prob_vector || {};
  const dist = pv.dist || {};
  const margin = dist.margin || {};
  const totalD = dist.total || {};
  const ml = pv.ML || {};
  const sp = pv.SPREAD || {};
  const tot = pv.TOTAL || {};
  const tt = pv.TEAM_TOTAL || {};

  return (
    <>
      <Tiles
        items={[
          { k: "Margin μ (home)", v: dec(margin.mu, 1) },
          { k: "Margin σ", v: dec(margin.sigma, 1) },
          { k: "Total μ", v: dec(totalD.mu, 1) },
          { k: "Total σ", v: dec(totalD.sigma, 1) },
          { k: "Family", v: margin.family ?? totalD.family ?? "—" },
        ]}
      />
      <div className="variant-grid">
        <MarketCard title="Moneyline">
          {ml.HOME == null && ml.AWAY == null ? (
            <span className="subtle">not priced</span>
          ) : (
            <>
              <Line k="Home win" v={pct(ml.HOME)} />
              <Line k="Away win" v={pct(ml.AWAY)} />
            </>
          )}
        </MarketCard>
        <MarketCard title="Spread (home line)">
          {sp.line == null ? (
            <span className="subtle">not priced</span>
          ) : (
            <>
              <Line k="Home line" v={signed(sp.line)} />
              <Line k="Home cover" v={pct(sp.HOME)} />
              <Line k="Away cover" v={pct(sp.AWAY)} />
            </>
          )}
        </MarketCard>
        <MarketCard title="Total">
          {tot.line == null ? (
            <span className="subtle">not priced</span>
          ) : (
            <>
              <Line k="Line" v={dec(tot.line, 1)} />
              <Line k="Over" v={pct(tot.OVER)} />
              <Line k="Under" v={pct(tot.UNDER)} />
            </>
          )}
        </MarketCard>
        <MarketCard title="Team totals">
          {tt.HOME == null && tt.AWAY == null ? (
            <span className="subtle">not priced</span>
          ) : (
            <>
              <Line
                k="Home"
                v={
                  tt.HOME
                    ? `${dec(tt.HOME.line, 1)} · over ${pct(tt.HOME.OVER)}`
                    : "—"
                }
              />
              <Line
                k="Away"
                v={
                  tt.AWAY
                    ? `${dec(tt.AWAY.line, 1)} · over ${pct(tt.AWAY.OVER)}`
                    : "—"
                }
              />
            </>
          )}
        </MarketCard>
      </div>
      <p className="page-sub">
        Model {prediction.model_version ?? "—"}. All probabilities are derived from the single
        stored distribution above — the market is efficient, and these are calibrated forecasts, not
        tips.
      </p>
    </>
  );
}

function PropsBlock({ props }) {
  const projections = props?.prop_predictions ?? [];
  const lines = props?.lines ?? [];
  const consensus = props?.consensus ?? [];
  if (!projections.length && !lines.length && !consensus.length) {
    return (
      <div className="card zero">
        No player-prop data stored for this game yet — projections, book lines, and the devig
        consensus all populate as captures arrive.
      </div>
    );
  }
  return (
    <>
      {projections.length ? (
        <section>
          <h2>Model projections</h2>
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
                </tr>
              </thead>
              <tbody>
                {projections.map((p, i) => (
                  <tr key={`${p.player}-${p.market_key}-${i}`}>
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {lines.length ? (
        <section>
          <h2>Book lines</h2>
          <p className="page-sub">
            Two-sided soft-book quotes and DFS legs. DFS legs carry no over/under price — they show
            a payout multiplier instead.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Market</th>
                  <th>Book</th>
                  <th className="num">Line</th>
                  <th className="num">Over</th>
                  <th className="num">Under</th>
                  <th className="num">Payout×</th>
                  <th>Capture</th>
                </tr>
              </thead>
              <tbody>
                {lines.map((l, i) => (
                  <tr key={`${l.player}-${l.market_key}-${l.book}-${i}`}>
                    <td className="fixture">{l.player ?? "—"}</td>
                    <td>
                      <span className="chip info">{l.market_key ?? "—"}</span>
                    </td>
                    <td className="subtle">
                      {l.book ?? "—"} {l.is_dfs ? <span className="chip dim">DFS</span> : null}
                    </td>
                    <td className="num">{dec(l.line, 1)}</td>
                    <td className="num">{odds(l.over_price)}</td>
                    <td className="num">{odds(l.under_price)}</td>
                    <td className="num">{l.payout_mult != null ? odds(l.payout_mult) : "—"}</td>
                    <td className="subtle">
                      {l.is_closing ? <span className="chip warn">close</span> : "open"}{" "}
                      {tipoffTime(l.captured_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {consensus.length ? (
        <section>
          <h2>Devig consensus (sharp fair)</h2>
          <p className="page-sub">
            The de-vigged sharp/consensus fair — the benchmark the edge engine measures every price
            against.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Market</th>
                  <th className="num">Line</th>
                  <th className="num">Fair over</th>
                  <th>Anchor</th>
                  <th>Capture</th>
                </tr>
              </thead>
              <tbody>
                {consensus.map((c, i) => (
                  <tr key={`${c.player}-${c.market_key}-${i}`}>
                    <td className="fixture">{c.player ?? "—"}</td>
                    <td>
                      <span className="chip info">{c.market_key ?? "—"}</span>
                    </td>
                    <td className="num">{dec(c.line, 1)}</td>
                    <td className="num">{pct(c.fair_prob_over)}</td>
                    <td className="subtle">{c.anchor ?? "—"}</td>
                    <td className="subtle">
                      {c.is_closing ? <span className="chip warn">close</span> : "open"}{" "}
                      {tipoffTime(c.captured_at)}
                    </td>
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

export default function GameDetail() {
  const { id } = useParams();
  const state = useApi(
    () =>
      Promise.all([fetchGamePrediction(id), fetchGameProps(id)]).then(([pred, props]) => ({
        pred,
        props,
      })),
    [id],
  );

  if (state.loading) return <Loading what="game detail" />;
  if (state.error) return <ErrorBox error={state.error} what="this game" />;

  const pred = state.data?.pred ?? {};
  const props = state.data?.props ?? {};
  const prediction = pred.prediction ?? null;
  const fixture = prediction?.fixture ?? `Game ${pred.game_id ?? id}`;

  return (
    <>
      <p className="page-sub">
        <Link to="/" className="row-link">
          ← back to today's predictions
        </Link>
      </p>
      <h1 className="page-title">
        {fixture} <GameStatusChip status={pred.status} />
      </h1>
      <p className="page-sub">
        {prediction?.league ? `${prediction.league} · ` : ""}Tip-off {tipoffFull(pred.tipoff_utc)}
      </p>
      <PaperBanner text="Research detail only — no line here is a bet, and no stake is placed." />

      <section>
        <h2>CORE prediction</h2>
        <PredictionBlock prediction={prediction} />
      </section>

      <PropsBlock props={props} />
    </>
  );
}
