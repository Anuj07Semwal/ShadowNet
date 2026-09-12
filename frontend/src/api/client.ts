import axios from "axios";

const configuredApiUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");

export const api = axios.create({
  baseURL: configuredApiUrl ? `${configuredApiUrl}/api` : "/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});