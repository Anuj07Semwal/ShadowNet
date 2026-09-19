import { AnimatePresence, motion } from "motion/react";
import { FileUp, Map, SearchCheck, Settings, ShieldCheck, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "../../auth/AuthContext";
import { useLanguage } from "../../i18n/LanguageContext";

export default function OnboardingTour() {
  const { session } = useAuth();
  const { t } = useLanguage();
  const key = `shadownet-tutorial-seen:${session?.username ?? "user"}`;
  const [open, setOpen] = useState(true);
  const [step, setStep] = useState(0);
  useEffect(() => {
    const replay = () => { setStep(0); setOpen(true); };
    window.addEventListener("shadownet:replay-tutorial", replay);
    return () => window.removeEventListener("shadownet:replay-tutorial", replay);
  }, [session, key]);
  const steps = [
    { icon: ShieldCheck, title: t("tutorialWelcome"), body: t("tutorialWelcomeBody") },
    { icon: FileUp, title: t("tutorialUpload"), body: t("tutorialUploadBody") },
    { icon: SearchCheck, title: t("tutorialInvestigate"), body: t("tutorialInvestigateBody") },
    { icon: Map, title: t("tutorialGraph"), body: t("tutorialGraphBody") },
    { icon: Settings, title: t("tutorialSettings"), body: t("tutorialSettingsBody") },
  ];
  function close() { localStorage.setItem(key, "yes"); setOpen(false); }
  const current = steps[step]; const Icon = current.icon;
  return <AnimatePresence>{open && <motion.div className="tour-scrim" role="dialog" aria-modal="true" aria-labelledby="tour-title" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}><motion.section className="tour-card" initial={{ opacity: 0, scale: .96, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: .97 }} transition={{ type: "spring", stiffness: 250, damping: 25 }}><button className="tour-close" type="button" onClick={close} aria-label={t("close")}><X /></button><div className="tour-progress" aria-label={`${step + 1} of ${steps.length}`}>{steps.map((_, index) => <span className={index <= step ? "active" : ""} key={index} />)}</div><span className="tour-icon"><Icon size={30} /></span><p className="eyebrow">{step + 1} / {steps.length}</p><h2 id="tour-title">{current.title}</h2><p>{current.body}</p><div className="tour-actions"><button type="button" onClick={close}>{t("skip")}</button>{step > 0 && <button type="button" onClick={() => setStep(step - 1)}>{t("back")}</button>}<button className="primary-action" type="button" onClick={() => step === steps.length - 1 ? close() : setStep(step + 1)}>{step === steps.length - 1 ? t("finish") : t("next")}</button></div></motion.section></motion.div>}</AnimatePresence>;
}
