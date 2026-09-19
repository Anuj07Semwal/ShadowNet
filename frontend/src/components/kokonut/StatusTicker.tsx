import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";

export default function StatusTicker({ items }: { items: string[] }) {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => setIndex((value) => (value + 1) % items.length), 3200);
    return () => window.clearInterval(timer);
  }, [items.length]);
  return <div className="status-ticker" aria-live="polite"><span className="status-pulse"/><AnimatePresence mode="wait"><motion.span key={items[index]} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: .2 }}>{items[index]}</motion.span></AnimatePresence></div>;
}
