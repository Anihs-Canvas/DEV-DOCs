// API client for /api/v1/* — the read-only paper surface over model
// predictions, published devig edge picks, and the forward-CLV gate. Every
// endpoint is AllowAny + read-only and sends Access-Control-Allow-Origin, so
// this app can fetch cross-port on localhost. Nothing here writes — the whole
// product is PAPER-ONLY by construction.
const API_BASE = (import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

// Raw network GET — the fetch primitive. Throws a helpful error on a dead
// server or a non-2xx response; returns parsed JSON otherwise.
async function getJson(path) {
  const url = `${API_BASE}${path}`;
  let response;
  try {
    response = await fetch(url, { headers: { Accept: "application/json" } });
  } catch (err) {
    throw new Error(
      `cannot reach the API at ${url} — is the Django dev server running? (${err.message})`,
    );
  }
  if (!response.ok) {
    let detail = "";
    try {
      detail = (await response.json()).detail ?? "";
    } catch {
      /* non-JSON error body */
    }
    throw new Error(`${response.status} from ${url}${detail ? ` — ${detail}` : ""}`);
  }
  return response.json();
}

// --- typed fetchers, one per documented endpoint --------------------------

// Team CORE predictions + player-prop projections for games tipping on `date`
// (YYYY-MM-DD; omitted = today, resolved server-side).
export const fetchPredictionsToday = (date) =>
  getJson(`/api/v1/predictions/today${date ? `?date=${encodeURIComponent(date)}` : ""}`);

// Currently OPEN published +EV edge picks (the devig / line-shop product).
export const fetchEdgeToday = () => getJson("/api/v1/edge/today");

// The EdgeRule (venue x market x league) grid + each cell's enabled flag.
// Every cell starts DISABLED and earns ON only via the forward-CLV gate.
export const fetchEdgeCells = () => getJson("/api/v1/edge/cells");

// The forward-CLV verdict grid over a trailing `days` window (default 90).
export const fetchClvGate = (days = 90) => getJson(`/api/v1/clv/gate?days=${days}`);

// One game's team CORE prediction (prob_vector + distribution params).
export const fetchGamePrediction = (gameId) => getJson(`/api/v1/games/${gameId}/prediction`);

// One game's prop board: model projections + book lines + devig consensus.
export const fetchGameProps = (gameId, market) =>
  getJson(`/api/v1/games/${gameId}/props${market ? `?market=${encodeURIComponent(market)}` : ""}`);

export { API_BASE };
