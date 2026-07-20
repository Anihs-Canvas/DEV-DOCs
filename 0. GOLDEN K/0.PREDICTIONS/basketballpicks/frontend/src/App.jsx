import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import Predictions from "./pages/Predictions.jsx";
import Edge from "./pages/Edge.jsx";
import ClvGate from "./pages/ClvGate.jsx";
import GameDetail from "./pages/GameDetail.jsx";

// PRIMARY = the honest model surface (calibrated CORE distribution). EDGE +
// GATE carry the arbitrage framing and the forward-CLV discipline, so they sit
// under their own de-emphasised group — the edge is a grind, not the headline.
const PRIMARY_NAV = [{ to: "/", end: true, label: "Today's predictions", ico: "▤" }];
const EDGE_NAV = [
  { to: "/edge", end: false, label: "Edge — +EV picks", ico: "✦" },
  { to: "/clv-gate", end: false, label: "Forward-CLV gate", ico: "✓" },
];

export default function App() {
  const [navOpen, setNavOpen] = useState(false); // mobile drawer only

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-head">
          <div className="brand">
            Basketball<em>Picks</em>
            <small>devig edge &amp; forward-CLV gate</small>
          </div>
          <button
            className="nav-toggle"
            type="button"
            aria-expanded={navOpen}
            aria-controls="side-nav"
            aria-label="Toggle navigation"
            onClick={() => setNavOpen((open) => !open)}
          >
            ☰
          </button>
        </div>
        <nav id="side-nav" className={`side-nav ${navOpen ? "open" : ""}`} aria-label="Pages">
          {PRIMARY_NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "active" : "")}
              onClick={() => setNavOpen(false)}
            >
              <span className="nav-ico" aria-hidden="true">
                {item.ico}
              </span>
              {item.label}
            </NavLink>
          ))}
          <div className="nav-section-label" role="presentation">
            Arbitrage grind — paper only
          </div>
          {EDGE_NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "active dim" : "dim")}
              onClick={() => setNavOpen(false)}
            >
              <span className="nav-ico" aria-hidden="true">
                {item.ico}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="app-main">
        <div className="topbar">
          <div className="status-strip" role="note">
            <span className="chip warn">PAPER-ONLY</span>
            <span className="subtle">no real stakes</span>
            <span className="dot" aria-hidden="true">
              ·
            </span>
            <span className="subtle">edge validated FORWARD via closing-line value</span>
            <span className="dot" aria-hidden="true">
              ·
            </span>
            <span className="subtle">not a bookmaker-beater</span>
          </div>
        </div>
        <main>
          <Routes>
            <Route path="/" element={<Predictions />} />
            <Route path="/edge" element={<Edge />} />
            <Route path="/clv-gate" element={<ClvGate />} />
            <Route path="/game/:id" element={<GameDetail />} />
          </Routes>
        </main>
        <footer>
          BasketballPicks is a research paper product. The CORE model publishes a calibrated
          margin/total distribution shown alongside the market for context — not betting advice.
          The edge layer is a devig / line-shop arbitrage grind validated forward via CLV; every
          gate cell starts DISABLED and no real stakes are placed.
        </footer>
      </div>
    </div>
  );
}
