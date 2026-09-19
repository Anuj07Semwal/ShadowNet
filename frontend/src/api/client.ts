import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
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
  (error) => {
    const detail = error?.response?.data?.detail;
    if (detail && typeof detail === "string") {
      error.userMessage = detail;
    } else if (!error?.response) {
      error.userMessage = "Cannot reach the backend. Confirm that FastAPI is running on port 8000.";
    } else {
      error.userMessage = "The request could not be completed. Please try again.";
    }
    return Promise.reject(error);
  }
);
