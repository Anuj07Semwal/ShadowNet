import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import { LanguageProvider, useLanguage } from "./i18n/LanguageContext";
import { AuthProvider } from "./auth/AuthContext";
import { MotionConfig } from "motion/react";
import { PreferencesProvider } from "./preferences/PreferencesContext";

const Cases = lazy(() => import("./pages/Cases"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Documents = lazy(() => import("./pages/Documents"));
const Investigation = lazy(() => import("./pages/Investigation"));
const LegalPage = lazy(() => import("./pages/LegalPage"));
const NetworkExplorer = lazy(() => import("./pages/NetworkExplorer"));
const NotFound = lazy(() => import("./pages/NotFound"));
const PersonInvestigation = lazy(() => import("./pages/PersonInvestigation"));
const Persons = lazy(() => import("./pages/Persons"));
const Settings = lazy(() => import("./pages/Settings"));

function PersonRoute() {
  return <PersonInvestigation />;
}

export default function App() {
  return (
    <MotionConfig reducedMotion="user"><PreferencesProvider><LanguageProvider><AuthProvider><AuthenticatedApp /></AuthProvider></LanguageProvider></PreferencesProvider></MotionConfig>
  );
}

function AuthenticatedApp() {
  const { t } = useLanguage();
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="state-panel" role="status">{t("working")}</div>}>
        <Routes>
            <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/persons" element={<Persons />} />
            <Route path="/persons/:personId" element={<PersonRoute />} />
            <Route path="/network" element={<NetworkExplorer />} />
            <Route path="/cases" element={<Cases />} />
            <Route path="/investigation" element={<Investigation />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/privacy" element={<LegalPage type="privacy" />} />
            <Route path="/terms" element={<LegalPage type="terms" />} />
            <Route path="/cookies" element={<LegalPage type="cookies" />} />
            <Route path="*" element={<NotFound />} />
            </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
