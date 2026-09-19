import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type ThemeChoice = "light" | "dark" | "system";

const PreferencesContext = createContext<{
  theme: ThemeChoice;
  resolvedTheme: "light" | "dark";
  setTheme: (theme: ThemeChoice) => void;
  motionEnabled: boolean;
  setMotionEnabled: (enabled: boolean) => void;
} | null>(null);

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<ThemeChoice>(() => {
    const saved = localStorage.getItem("shadownet-theme");
    return saved === "light" || saved === "dark" || saved === "system" ? saved : "system";
  });
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches);
  const [motionEnabled, setMotionEnabled] = useState(true);
  const resolvedTheme = theme === "system" ? (systemDark ? "dark" : "light") : theme;

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const update = () => setSystemDark(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    localStorage.setItem("shadownet-theme", theme);
    document.documentElement.dataset.theme = resolvedTheme;
  }, [theme, resolvedTheme]);

  useEffect(() => {
    localStorage.setItem("shadownet-motion", motionEnabled ? "on" : "off");
    document.documentElement.dataset.motion = motionEnabled ? "on" : "off";
  }, [motionEnabled]);

  const value = useMemo(
    () => ({ theme, resolvedTheme, setTheme, motionEnabled, setMotionEnabled }),
    [theme, resolvedTheme, motionEnabled],
  );
  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePreferences() {
  const value = useContext(PreferencesContext);
  if (!value) throw new Error("usePreferences must be used within PreferencesProvider");
  return value;
}
