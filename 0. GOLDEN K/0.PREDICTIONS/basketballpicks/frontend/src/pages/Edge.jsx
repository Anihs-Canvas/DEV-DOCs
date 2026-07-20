// Page 2 — Edge (+EV picks). The DEVIG-CENTRIC product: the benchmark is the
// sharp/consensus fair probability, and a pick exists only when a soft-book or
// DFS price beats it by the pre-registered edge floor. model_prob is a
// secondary (often null) input, never the headline. Honestly framed at the top
// as an arbitrage grind, paper-only, forward-validated. Zero picks is a
// designed state. The EdgeRule grid shows every cell DISABLED by default.
import { fetchEdgeCells, fetchEdgeToday } from "../api.js";
import {
  EdgeHonestyBanner,
  EnabledChip,
  ErrorBox,
  InfoBanner,
  Loading,
  PaperBanner,
  Tiles,
  useApi,
} from "../components.jsx";
import { dec, int, odds, pct, signed, signedPct, tipoffFull } from "../format.js";

export default function Edge() {
  const state = useApi(
    () =>
      Promise.all([fetchEdgeToday(), fetchEdgeCells()]).then(([today, cells]) => ({ today, cells })),
    [],
  );

  if (state.loading) return <Loading what="the edge board" />;
  if (state.error) return <ErrorBox error={state.error} what="edge picks" />;

  const today = state.data?.today ?? {};
  const cellsData = state.data?.cells ?? {};
  const picks = today.picks ?? [];
  const cells = cellsData.cells ?? [];
  const enabledCount = cells.filter((c) => c.enabled).length;
  const notMigrated = Boolean(today.detail); // "edge app not migrated yet"

  return (
    <>
      <h1 className="page-title">Edge — devig +EV picks</h1>
      <EdgeHonestyBanner />
      <PaperBanner text="Published picks are recorded at flag-time for forward-CLV measurement only. No stake is placed." />

      {notMigrated ? (
        <InfoBanner
          title="Edge engine not fully wired yet"
          text={`The API reports: ${today.detail}. The board below is the honest empty state until it is.`}
        />
      ) : null}

      <Tiles
        items={[
          { k: "Open picks", v: int(today.count ?? picks.length) },
          { k: "Rule cells", v: int(cellsData.count ?? cells.length) },
          { k: "Cells enabled", v: int(enabledCount), tone: enabledCount ? "" : "" },
          { k: "Paper only", v: "YES" },
        ]}
      />

      <section>
        <h2>Open +EV picks</h2>
        <p className="page-sub">
          Benchmark = the sharp/consensus <strong>fair</strong> probability at the price we could
          take. <strong>Edge</strong> and <strong>EV</strong> are measured against that fair, not
          against our model — the model probability is a secondary, often-null input shown for
          context only.
        </p>
        {picks.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Match</th>
                  <th>Venue</th>
                  <th>Player / market</th>
                  <th>Side · line</th>
                  <th>Book</th>
                  <th className="num">Sharp fair</th>
                  <th className="num">Book devig</th>
                  <th className="num">Edge</th>
                  <th className="num">EV</th>
                  <th className="num">Model p</th>
                  <th className="num">Min price</th>
                  <th>Expires</th>
                </tr>
              </thead>
              <tbody>
                {picks.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <span className="fixture">{p.fixture ?? "—"}</span>{" "}
                      <span className="subtle">{p.league ?? ""}</span>
                    </td>
                    <td>
                      <span className="chip dim">{p.venue ?? "—"}</span>
                    </td>
                    <td>
                      {p.player ? <span className="fixture">{p.player}</span> : <span className="subtle">team</span>}{" "}
                      <span className="chip info">{p.market_key ?? "—"}</span>
                    </td>
                    <td>
                      {p.side ?? "—"}
                      {p.line != null ? <span className="subtle"> {dec(p.line, 1)}</span> : null}
                    </td>
                    <td className="subtle">{p.book ?? "—"}</td>
                    <td className="num">{pct(p.sharp_fair_prob)}</td>
                    <td className="num">{pct(p.book_implied_devig)}</td>
                    <td className="num pos">{signedPct(p.edge)}</td>
                    <td className="num">{signedPct(p.ev)}</td>
                    <td className="num subtle">{p.model_prob != null ? pct(p.model_prob) : "—"}</td>
                    <td className="num">{odds(p.min_acceptable_price)}</td>
                    <td className="subtle">{tipoffFull(p.expires_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card zero">
            <strong>No open +EV picks right now — this is a designed state.</strong>
            <div className="label">
              A pick exists only when a real soft/DFS price beats the sharp fair by the frozen edge
              floor. Zero picks means the market is efficient today — not an error, and never
              back-filled.
            </div>
          </div>
        )}
      </section>

      <section>
        <h2>Rule cells — every cell starts DISABLED</h2>
        <p className="page-sub">
          The (venue × market × league) grid. A cell only flips <span className="chip warn">ENABLED</span>{" "}
          via a dated ADR after the forward-CLV gate returns CONFIRM. Default is{" "}
          <span className="chip dim">DISABLED</span>.
        </p>
        {cells.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Cell</th>
                  <th>Venue</th>
                  <th>Market</th>
                  <th>League level</th>
                  <th className="num">Min edge</th>
                  <th>State</th>
                </tr>
              </thead>
              <tbody>
                {cells.map((c) => (
                  <tr key={c.cell}>
                    <td className="subtle">{c.cell ?? "—"}</td>
                    <td>
                      <span className="chip dim">{c.venue ?? "—"}</span>
                    </td>
                    <td>
                      <span className="chip info">{c.market ?? "—"}</span>
                    </td>
                    <td className="subtle">{c.league_level ?? "—"}</td>
                    <td className="num">{c.min_edge != null ? signedPct(c.min_edge) : "—"}</td>
                    <td>
                      <EnabledChip enabled={c.enabled} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card zero">
            No rule cells defined yet — the grid populates once the edge app is migrated. Until
            then there is nothing to enable, which is the correct (safe) default.
          </div>
        )}
      </section>
    </>
  );
}
