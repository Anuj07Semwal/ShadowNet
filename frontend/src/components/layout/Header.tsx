import { useEffect, useState, type FormEvent } from "react";
import { CircleHelp, LogOut, Menu, Search } from "lucide-react";

import { api } from "../../api/client.ts";
import { useLanguage } from "../../i18n/LanguageContext";
import { useAuth } from "../../auth/AuthContext";

interface HeaderProps {
  onSearch: (value: string) => void;
  onMenu: () => void;
}

export default function Header({ onSearch, onMenu }: HeaderProps) {
  const { t } = useLanguage();
  const { logout } = useAuth();
  const [query, setQuery] = useState("");
  const [connected, setConnected] = useState<boolean | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.get("/health").then(() => setConnected(true)).catch(() => setConnected(false));
  }, []);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (query.trim().length < 2) {
      setMessage(t("minimumSearch"));
      return;
    }
    setMessage("");
    onSearch(query);
  }

  return (
    <header className="topbar">
      <button className="icon-button mobile-menu" onClick={onMenu} aria-label={t("menu")} type="button">
        <Menu size={22} />
      </button>
      <div className="header-actions">
        <form className="global-search" onSubmit={submit} role="search">
          <Search size={17} aria-hidden="true" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t("search")}
            aria-label={t("search")}
          />
          <button type="submit">{t("searchAction")}</button>
          {message && <span className="field-message error-text" role="alert">{message}</span>}
        </form>
        <span className={`connection-state ${connected === false ? "offline" : ""}`}>
          <span aria-hidden="true" />
          {connected === null ? t("checking") : connected === false ? t("disconnected") : t("connected")}
        </span>
        <button className="guide-button" type="button" onClick={() => window.dispatchEvent(new Event("shadownet:open-page-guide"))}><CircleHelp size={17} />{t("guide")}</button>
        <button className="logout-button" type="button" onClick={() => void logout().catch(() => undefined)} aria-label={t("signOut")}><LogOut size={17} /></button>
      </div>
    </header>
  );
}
