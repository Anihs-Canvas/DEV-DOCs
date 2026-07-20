// Shared presentational pieces + the standing HONESTY surfaces. Every table
// lives inside .table-wrap so wide content scrolls in its own container.
// The banners below are non-negotiable: this product is a devig / line-shop
// arbitrage grind validated FORWARD via closing-line value, PAPER-ONLY, and
// NOT a bookies-beater. Nothing on screen may overstate the model.
import { useEffect, useState } from "react";

// --- tiny data-loading hook (keeps every page's loading/error/data uniform) --
export function useApi(fetcher, deps) {
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    let cancelled = false;
    setState({ loading: true, error: null, data: null });
    fetcher()
      .then((data) => !cancelled && setState({ loading: false, error: null, data }))
      .catch((error) => !cancelled && setState({ loading: false, error, data: null }));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}

export function Loading({ what }) {
  return <div className="loading">Loading {what}…</div>;
}

export function ErrorBox({ error, what }) {
  return (
    <div className="error-box">
      Could not load {what}: <code>{error?.message ?? "unknown error"}</code>
    </div>
  );
}

// --- standing banners ------------------------------------------------------

export function PaperBanner({ text }) {
  return (
    <div className="banner paper" role="note">
      <strong>PAPER-ONLY — no real money, no real stakes</strong>
      {text}
    </div>
  );
}

export function DangerBanner({ title, text, children }) {
  return (
    <div className="banner danger" role="note">
      <strong>{title}</strong>
      {text}
      {children}
    </div>
  );
}

export function InfoBanner({ title, text, children }) {
  if (!title && !text && !children) return null;
  return (
    <div className="banner info" role="note">
      {title ? <strong>{title}</strong> : null}
      {text}
      {children}
    </div>
  );
}

// The one honesty banner the whole edge/CLV product hangs on. Rendered at the
// top of the Edge and CLV-gate pages, verbatim in spirit every time.
export function EdgeHonestyBanner() {
  return (
    <DangerBanner title="Read this first — what this edge is, and is not">
      These picks are a <strong>devig / line-shop ARBITRAGE grind</strong>: we take a soft-book or
      DFS price the sharp/consensus fair says is mispriced. This is <strong>NOT a model that
      beats the bookmaker</strong> and not a tip service. Every pick is validated{" "}
      <strong>FORWARD, via closing-line value (CLV)</strong> — did the market move toward us by
      lock? Until a cell earns a CONFIRM verdict it stays <strong>DISABLED</strong>. Everything
      here is <strong>PAPER-ONLY</strong>; no real stakes have been, or will be, placed at this
      gate state.
    </DangerBanner>
  );
}

// --- status chips (status = colour + TEXT, never colour alone) -------------

const VERDICT_CLASS = { CONFIRM: "good", KILL: "crit", HOLD: "dim" };

export function VerdictChip({ verdict }) {
  if (!verdict) return null;
  return (
    <span
      className={`chip ${VERDICT_CLASS[verdict] ?? "dim"}`}
      title="Pre-registered forward-CLV verdict. CONFIRM is a RECOMMENDATION only — it never auto-enables a cell."
    >
      {verdict}
    </span>
  );
}

// The default-DISABLED flag every EdgeRule cell carries. null (no matching
// rule) reads as DISABLED — the honest default, never a silent gap.
export function EnabledChip({ enabled }) {
  if (enabled === true) {
    return (
      <span
        className="chip warn"
        title="Live-enabled — only reachable via a dated ADR after a CONFIRM verdict."
      >
        ENABLED
      </span>
    );
  }
  return (
    <span
      className="chip dim"
      title="Default state — every cell starts DISABLED and earns ON only via the forward-CLV gate."
    >
      DISABLED
    </span>
  );
}

// The calibrate-vs-noise gate on a prop projection. Noise markets are stored
// for devig DISPLAY only and are never trusted as our own edge.
export function CalibrationChip({ gate }) {
  if (gate === true) {
    return (
      <span className="chip good" title="Cleared the calibrate-vs-noise gate — trusted projection.">
        calibrated
      </span>
    );
  }
  if (gate === false) {
    return (
      <span
        className="chip warn"
        title="Noise market — stored for devig display only; never used as our own edge."
      >
        devig-only
      </span>
    );
  }
  return null;
}

const STATUS_CLASS = { FINAL: "dim", LIVE: "good", SCHEDULED: "info" };

export function GameStatusChip({ status }) {
  if (!status) return null;
  return <span className={`chip ${STATUS_CLASS[status] ?? "info"}`}>{status}</span>;
}

// A labelled stat tile grid — reused across pages for headline numbers.
export function Tiles({ items }) {
  if (!items?.length) return null;
  return (
    <div className="tiles">
      {items.map((it) => (
        <div className="tile" key={it.k}>
          <div className="k">{it.k}</div>
          <div className={`v ${it.tone ?? ""}`}>{it.v}</div>
        </div>
      ))}
    </div>
  );
}
