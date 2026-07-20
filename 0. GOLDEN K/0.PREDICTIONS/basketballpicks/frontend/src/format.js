// Display helpers — numbers stay honest. The DRF API sends DecimalFields as
// JSON STRINGS ("12.500", "0.54200") while prob_vector values are raw floats,
// so every helper coerces first and renders "—" for null/blank/non-numeric.

// Coerce anything the API might send (number, decimal-string, null) to a finite
// Number, else null. The single guard the whole module funnels through.
export const num = (value) => {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
};

// A probability in [0,1] as a percentage with one decimal.
export const pct = (p, digits = 1) => {
  const n = num(p);
  return n === null ? "—" : `${(n * 100).toFixed(digits)}%`;
};

// A signed percentage of a fraction (edge / EV / CLV means): +4.5% / -1.2%.
export const signedPct = (value, digits = 1) => {
  const n = num(value);
  if (n === null) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${(n * 100).toFixed(digits)}%`;
};

// Decimal odds / payout multiplier: 2-3 sig places under 10, 1 above.
export const odds = (value) => {
  const n = num(value);
  if (n === null) return "—";
  return n.toFixed(n < 10 ? 2 : 1);
};

// A plain number to `digits` places (proj minutes, projected mean, points).
export const dec = (value, digits = 1) => {
  const n = num(value);
  return n === null ? "—" : n.toFixed(digits);
};

// A signed points value (line-move CLV, spread line): +1.5 / -0.5 / 0.0.
export const signed = (value, digits = 1) => {
  const n = num(value);
  if (n === null) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}`;
};

// An integer count (n, weeks, settled). "—" for missing, never NaN.
export const int = (value) => {
  const n = num(value);
  return n === null ? "—" : String(Math.round(n));
};

export const tipoffTime = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")} UTC`;
};

export const tipoffFull = (iso) => (iso ? `${String(iso).slice(0, 10)} ${tipoffTime(iso)}` : "—");

// A short human date label for a YYYY-MM-DD string.
export const dayLabel = (iso) => {
  if (!iso) return "—";
  const d = new Date(`${String(iso).slice(0, 10)}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
};
