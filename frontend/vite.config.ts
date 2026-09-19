import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],

  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: ["localhost", "127.0.0.1", "terminal.local"],
    headers: {
      "X-Content-Type-Options": "nosniff",
      "Referrer-Policy": "no-referrer",
      "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    },

    proxy: {
      "/api": {
        // Use the same IPv4 address Uvicorn binds to on Windows. Using
        // `localhost` can resolve to ::1 and make a healthy backend appear offline.
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
