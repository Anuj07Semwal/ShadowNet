import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

let csrfToken = "";

export function setCsrfToken(token: string) {
  csrfToken = token;
}

api.interceptors.request.use((config) => {
  if (csrfToken && config.method && !["get", "head", "options"].includes(config.method.toLowerCase())) {
    config.headers.set("X-CSRF-Token", csrfToken);
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error?.config as (typeof error.config & { __retryCount?: number }) | undefined;
    // Cold-start retry handling for idempotent GET requests
    if (config && (!config.method || config.method.toLowerCase() === "get")) {
      config.__retryCount = config.__retryCount || 0;
      const status = error?.response?.status;
      const isColdStart = !error.response || (status !== undefined && [502, 503, 504].includes(status));
      if (isColdStart && config.__retryCount < 5) {
        config.__retryCount += 1;
        await new Promise((resolve) => setTimeout(resolve, 3000));
        return api(config);
      }
    }

    const detail = error?.response?.data?.detail;
    if (detail && typeof detail === "string") {
      error.userMessage = detail;
    } else if (!error?.response) {
      error.userMessage = "Cannot reach the backend. If the service was asleep, it may take a minute to wake up.";
    } else {
      error.userMessage = "The request could not be completed. Please try again.";
    }
    return Promise.reject(error);
  }
);
