import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import Footer from "./Footer";
import Header from "./Header";
import Sidebar from "./Sidebar";
import OnboardingTour from "../onboarding/OnboardingTour";
import AmbientInvestigationBackground from "../motion-primitives/AmbientInvestigationBackground";
import PageGuide from "../onboarding/PageGuide";
import { useAuth } from "../../auth/AuthContext";
import { useLanguage } from "../../i18n/LanguageContext";

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { session } = useAuth();
  const { t } = useLanguage();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    // Closing mobile navigation after a route change keeps focus and layout predictable.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [location.pathname]);

  function handleSearch(value: string) {
    const query = value.trim();
    if (!query) return;
    navigate(`/persons?search=${encodeURIComponent(query)}`);
  }

  return (
    <div className="app-shell">
      <AmbientInvestigationBackground />
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <Header onSearch={handleSearch} onMenu={() => setMenuOpen(true)} />
      <div className="content-column">
        {session?.password_review_due && <div className="password-alert" role="status">{t("passwordReminder")} <button onClick={() => navigate("/settings")}>{t("passwordSecurity")}</button></div>}
        <main id="main-content" className="page-content"><PageGuide key={location.pathname} /><Outlet /></main>
        <Footer />
      </div>
      <OnboardingTour />
    </div>
  );
}
