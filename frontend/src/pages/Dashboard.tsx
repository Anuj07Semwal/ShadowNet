import { FileCheck2, FolderSearch2, RefreshCw, ShieldAlert, UserRoundCheck } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getWorkspaceDashboard, type WorkspaceDashboard } from "../api/workspace.ts";
import { useLanguage } from "../i18n/LanguageContext";
import { readableText } from "../utils/displayLabels";

export default function Dashboard() {
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const [data, setData] = useState<WorkspaceDashboard | null>(null);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    getWorkspaceDashboard().then(setData).catch(() => setError(t("backendReason")));
  }, [retry, t]);

  if (error) return <div className="state-panel state-error" role="alert"><ShieldAlert size={30} /><div><h2>{t("backendError")}</h2><p>{error}</p></div><button type="button" onClick={() => { setError(""); setData(null); setRetry((v) => v + 1); }}><RefreshCw size={17} />{t("retry")}</button></div>;
  if (!data) return <div className="state-panel" role="status">{t("loadingFir")}...</div>;

  const cards = [
    { label: t("myInvestigations"), value: data.investigation_count, icon: FolderSearch2, color: "blue" },
    { label: t("myUploads"), value: data.upload_count, icon: FileCheck2, color: "green" },
    { label: t("evidenceMatches"), value: data.evidence_match_count, icon: ShieldAlert, color: "orange" },
    { label: t("workspaceOwner"), value: data.username, icon: UserRoundCheck, color: "red" },
  ];

  return <div className="dashboard-page">
    <motion.section className="welcome-strip evidence-board" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ type: "spring", stiffness: 180, damping: 22 }}>
      <div><p className="eyebrow">{t("dashboardEyebrow")}</p><h1>{t("dashboardTitle")}, {data.username}</h1><p>{t("dashboardIntro")}</p></div>
      <button type="button" onClick={() => navigate("/investigation")}>{t("startInvestigation")}</button>
    </motion.section>

    <section className="metric-grid" aria-label="Personal workspace summary">
      {cards.map(({ label, value, icon: Icon, color }, index) => <motion.article className={`metric-card metric-${color}`} key={label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .05 }} whileHover={{ y: -3 }}><span><Icon size={21} /></span><div><p>{label}</p><strong>{value}</strong></div></motion.article>)}
    </section>

    <section className="data-panel personal-activity">
      <div className="panel-heading"><div><h2>{t("recentActivity")}</h2><p>{t("recentActivityHint")}</p></div><button type="button" onClick={() => navigate("/investigation")}>{t("openInvestigation")}</button></div>
      {data.recent_investigations.length ? <div className="activity-list">{data.recent_investigations.slice(0, 8).map((item) => <article key={item.id}><div><strong>{readableText(item.question, language)}</strong><small>{new Date(item.created_at).toLocaleString()}</small></div><span>{item.matching_records} {t("evidenceMatches")}</span></article>)}</div> : <div className="empty-workspace"><FolderSearch2 size={36} /><h3>{t("noActivity")}</h3><p>{t("noActivityBody")}</p><div><button onClick={() => navigate("/documents")} type="button">{t("documents")}</button><button onClick={() => navigate("/investigation")} type="button">{t("startInvestigation")}</button></div></div>}
    </section>
  </div>;
}
