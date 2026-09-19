import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, setCsrfToken } from "../api/client.ts";

export interface Session { username: string; role: string; csrf_token: string; password_age_days: number; password_review_days: number; password_review_due: boolean }

const AuthContext = createContext<{
  session: Session | null;
  checking: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
} | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [checking, setChecking] = useState(() => sessionStorage.getItem("shadownet-active") === "yes");

  useEffect(() => {
    if (sessionStorage.getItem("shadownet-active") !== "yes") {
      return;
    }
    api.get<Session>("/auth/session")
      .then((response) => { setSession(response.data); setCsrfToken(response.data.csrf_token); })
      .catch(() => { setSession(null); setCsrfToken(""); })
      .finally(() => setChecking(false));
  }, []);

  async function login(username: string, password: string) {
    const response = await api.post<Session>("/auth/login", { username, password });
    setSession(response.data);
    setCsrfToken(response.data.csrf_token);
    sessionStorage.setItem("shadownet-active", "yes");
  }

  async function logout() {
    try { await api.post("/auth/logout"); }
    finally { setSession(null); setCsrfToken(""); sessionStorage.removeItem("shadownet-active"); }
  }

  const value = useMemo(() => ({ session, checking, login, logout }), [session, checking]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Context hooks intentionally share this module with their provider.
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
