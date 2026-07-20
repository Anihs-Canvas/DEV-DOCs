import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// BasketballPicks Frontend v1. The API origin comes from VITE_API_BASE
// (.env commits the Django dev default; shell env wins).
export default defineConfig({
  plugins: [react()],
});
