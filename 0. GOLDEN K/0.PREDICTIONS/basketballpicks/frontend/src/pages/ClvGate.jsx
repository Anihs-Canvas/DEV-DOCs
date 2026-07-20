// Page 3 — the forward-CLV gate. This is the honesty discipline: for every
// pick we would flag as +EV, we record it at flag-time and, at lock, measure
// whether the market moved TOWARD us (closing-line value). Forward-only by
// construction — empty until open->closing prop pairs accrue. The per-cell
// verdict is CONFIRM / KILL / HOLD, but a CONFIRM is a RECOMMENDATION only:
// every cell starts DISABLED and is never auto-enabled here.
import { useState } from "react";
import { fetchClvGate } from "../api.js";
import {
  DangerBanner,
  EnabledChip,
  ErrorBox,
  Loading,
  PaperBanner,
  Tiles,
  useApi,
  VerdictChip,
} from "../components.jsx";
import { dec, int, signed, signedPct } from "../format.js";

const DAY_OPTIONS = [30, 60, 90, 180];

// Object-of-summaries -> array, CONFIRM first, then KILL, then by -n (mirrors
// the Django dashboard's own ordering).
function toRows(obj) {
  const rows = Object.entries(obj ?? {}).map(([key, summ]) => ({ key, ...summ }));
  rows.sort(
    (a, b) =>
      (a.verdict !== "CONFIRM") - (b.verdict !== "CONFIRM") ||
      (a.verdict !== "KILL") - (b.verdict !== "KILL") ||
      (b.n ?? 0) - (a.n ?? 0),
  );
  return rows;
}

// A CI as "lo … hi" in signed-percent, or "—" when not yet estimable.
function ci(lo, hi) {
  if (lo == null && hi == null) return "—";
  return `${signedPct(lo)} … ${signedPct(hi)}`;
}

function SummaryTable({ title, rows, keyLabel, showEnabled }) {
  if (!rows.length) return null;
  return (
    <section>
      <h2>{title}</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{keyLabel}</th>
              <th className="num">n</th>
              <th className="num">sharp-beat n</th>
              <th className="num">Sharp-beat CLV</th>
              <th className="num">95% CI</th>
              <th className="num">Line-move</th>
              <th className="num">Weeks</th>
              <th className="num">ROI</th>
              <th>Verdict</th>
              {showEnabled ? <th>Cell state</th> : null}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.key}>
                <td className="subtle">{r.key}</td>
                <td className="num">{int(r.n)}</td>
                <td className="num">{int(r.n_sharp_beat)}</td>
                <td className="num">{signedPct(r.sharp_beat_mean)}</td>
                <td className="num subtle">{ci(r.sharp_beat_ci_lo, r.sharp_beat_ci_hi)}</td>
                <td className="num">{signed(r.line_move_mean, 2)}</td>
                <td className="num">{int(r.weeks)}</td>
                <td className="num">{signedPct(r.roi_mean)}</td>
                <td>
                  <VerdictChip verdict={r.verdict} />
                </td>
                {showEnabled ? (
                  <td>
                    <EnabledChip enabled={r.edge_rule_enabled} />
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function ClvGate() {
  const [days, setDays] = useState(90);
  const state = useApi(() => fetchClvGate(days), [days]);

  if (state.loading) return <Loading what="the forward-CLV gate" />;
  if (state.error) return <ErrorBox error={state.error} what="the CLV gate" />;

  const report = state.data ?? {};
  const overall = report.overall ?? {};
  const th = report.thresholds ?? {};
  const cellRows = toRows(report.by_cell);
  const venueRows = toRows(report.by_venue);
  const marketRows = toRows(report.by_market);
  const empty = (report.n_flagged ?? 0) === 0;

  return (
    <>
      <h1 className="page-title">Forward-CLV gate</h1>
      <DangerBanner title="A verdict is a recommendation — it never enables anything">
        This gate is <strong>forward-only</strong>: it measures whether the market moved toward each
        flagged pick by lock. A <strong>CONFIRM</strong> verdict is a{" "}
        <strong>recommendation to consider enabling a cell via a dated ADR</strong> — it does{" "}
        <strong>not</strong> auto-enable anything. Every cell starts, and stays,{" "}
        <span className="chip dim">DISABLED</span> until a human acts. Empty numbers today are
        correct: pairs accrue forward.
      </DangerBanner>
      <PaperBanner text="Every flagged pick is recorded, not staked. This grid decides nothing on its own." />

      <div className="anchor-bar" role="group" aria-label="Trailing window">
        <span className="subtle" style={{ marginRight: 4 }}>
          Window:
        </span>
        {DAY_OPTIONS.map((d) => (
          <button
            key={d}
            className={`anchor-btn ${days === d ? "on" : ""}`}
            onClick={() => setDays(d)}
          >
            {d}d
          </button>
        ))}
      </div>

      <Tiles
        items={[
          { k: "Games scanned", v: int(report.n_games_scanned) },
          { k: "Games with pairs", v: int(report.n_games_with_pairs) },
          { k: "Flagged picks", v: int(report.n_flagged) },
          { k: "Sharp-beat CLV", v: signedPct(overall.sharp_beat_mean) },
          { k: "Overall verdict", v: overall.verdict ?? "—" },
        ]}
      />

      {report.window ? (
        <p className="page-sub">
          Window {report.window.from} → {report.window.to}. Overall 95% CI on sharp-beat CLV:{" "}
          {ci(overall.sharp_beat_ci_lo, overall.sharp_beat_ci_hi)} over{" "}
          {int(overall.n_sharp_beat)} measured picks across {int(overall.weeks)} weeks.
        </p>
      ) : null}

      {empty ? (
        <div className="card zero">
          <strong>No flagged picks in this window yet — the expected forward-only state.</strong>
          <div className="label">
            The gate fills in only as games accrue BOTH an open and a closing prop capture plus a
            sharp/consensus fair. Nothing is simulated to populate it early.
          </div>
        </div>
      ) : (
        <>
          <SummaryTable
            title="Per-cell verdict grid (venue × market × league)"
            rows={cellRows}
            keyLabel="Cell"
            showEnabled
          />
          <SummaryTable title="By venue" rows={venueRows} keyLabel="Venue" />
          <SummaryTable title="By market" rows={marketRows} keyLabel="Market" />
        </>
      )}

      <section>
        <h2>Pre-registered thresholds (frozen)</h2>
        <p className="page-sub">
          These constants were committed BEFORE data collection and move only via a dated ADR —
          never tuned to rescue a cell. Shown in full so the discipline is auditable.
        </p>
        <div className="table-wrap">
          <table>
            <tbody>
              <tr>
                <td>Flag edge floor</td>
                <td className="num">{signedPct(th.flag_edge_min)}</td>
                <td>CONFIRM min n</td>
                <td className="num">{int(th.confirm_min_n)}</td>
              </tr>
              <tr>
                <td>CONFIRM min sharp-beat</td>
                <td className="num">{signedPct(th.confirm_min_sharp_beat)}</td>
                <td>CONFIRM min weeks</td>
                <td className="num">{int(th.confirm_min_weeks)}</td>
              </tr>
              <tr>
                <td>CONFIRM ROI CI floor</td>
                <td className="num">{signedPct(th.confirm_roi_ci_floor)}</td>
                <td>KILL min n</td>
                <td className="num">{int(th.kill_min_n)}</td>
              </tr>
              <tr>
                <td>KILL sharp-beat CI upper</td>
                <td className="num">{signedPct(th.kill_sharp_beat_ci_upper)}</td>
                <td>Bootstrap seed</td>
                <td className="num">{int(th.bootstrap_seed)}</td>
              </tr>
              <tr>
                <td>Flag leagues</td>
                <td className="subtle" colSpan={3}>
                  {(th.flag_leagues ?? []).join(", ") || "—"}
                </td>
              </tr>
              <tr>
                <td>Flag markets</td>
                <td className="subtle" colSpan={3}>
                  {(th.flag_markets ?? []).join(", ") || "—"}
                </td>
              </tr>
              <tr>
                <td>Anchor preference</td>
                <td className="subtle" colSpan={3}>
                  {(th.anchor_preference ?? []).join(" › ") || "—"}
                </td>
              </tr>
              <tr>
                <td>All cells start disabled</td>
                <td className="subtle" colSpan={3}>
                  {th.all_cells_start_disabled === false ? "no" : "YES — enforced"}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
