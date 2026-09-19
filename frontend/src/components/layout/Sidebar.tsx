import {
  FileText, LayoutDashboard, Network, Search,
  Settings, Shield, Users, X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { useLanguage } from "../../i18n/LanguageContext";
import BrandLogo from "../BrandLogo";

const navigation = [
  { key: "dashboard", path: "/", icon: LayoutDashboard },
  { key: "network", path: "/network", icon: Network },
  { key: "cases", path: "/cases", icon: Search },
  { key: "persons", path: "/persons", icon: Users },
  { key: "investigation", path: "/investigation", icon: Shield },
  { key: "documents", path: "/documents", icon: FileText },
  { key: "settings", path: "/settings", icon: Settings },
] as const;

export default function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useLanguage();
  return (
    <>
      {open && <button className="nav-scrim" onClick={onClose} aria-label={t("closeMenu")} type="button" />}
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <BrandLogo className="brand-mark" />
          <div><strong>ShadowNet</strong></div>
          <button className="icon-button close-menu" onClick={onClose} aria-label={t("closeMenu")} type="button"><X size={20} /></button>
        </div>
        <nav aria-label="Main navigation">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.path} to={item.path} end={item.path === "/"}>
                <Icon size={19} aria-hidden="true" />
                <span>{t(item.key)}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
