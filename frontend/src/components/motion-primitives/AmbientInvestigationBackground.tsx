import { motion } from "motion/react";
import { usePreferences } from "../../preferences/PreferencesContext";

export default function AmbientInvestigationBackground() {
  const { motionEnabled } = usePreferences();
  return <div className="moving-backdrop" aria-hidden="true">
    {motionEnabled && <>
      <motion.span className="ambient-signal signal-one" animate={{ x: [0, 35, 0], y: [0, -18, 0], opacity: [.2, .5, .2] }} transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }} />
      <motion.span className="ambient-signal signal-two" animate={{ x: [0, -26, 0], y: [0, 22, 0], opacity: [.15, .42, .15] }} transition={{ duration: 13, repeat: Infinity, ease: "easeInOut" }} />
      <motion.span className="ambient-link" animate={{ rotate: [-8, 5, -8], scaleX: [.92, 1.08, .92] }} transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }} />
    </>}
  </div>;
}
