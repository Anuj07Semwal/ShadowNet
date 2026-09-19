import { AnimatePresence, motion } from "motion/react";
import { Bot, FileSearch, Send, X } from "lucide-react";
import { useState, type FormEvent } from "react";
import { api } from "../../api/client.ts";
import { useLanguage } from "../../i18n/LanguageContext";

interface Result { answer: string; document_evidence?: unknown[]; graph_evidence?: unknown[] }

export default function InvestigatorAssistant() {
  const { language, t } = useLanguage();
  const [open, setOpen] = useState(false); const [question, setQuestion] = useState("");
  const [result, setResult] = useState<Result | null>(null); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  async function submit(event: FormEvent) { event.preventDefault(); if (question.trim().length < 4) return; setLoading(true); setError(""); try { setResult((await api.post<Result>("/graph-rag/investigate", { question, language })).data); setQuestion(""); } catch { setError(t("backendReason")); } finally { setLoading(false); } }
  return <><motion.button className="assistant-launcher" type="button" onClick={() => setOpen(!open)} whileHover={{ y: -3 }} whileTap={{ scale: .96 }} aria-label={t("askAssistant")}><Bot /><span>{t("askAssistant")}</span></motion.button><AnimatePresence>{open && <motion.aside className="assistant-panel" initial={{ opacity: 0, y: 20, scale: .97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 12, scale: .98 }} transition={{ type: "spring", stiffness: 260, damping: 26 }}><header><span><Bot /></span><div><strong>{t("assistant")}</strong><small>{t("secureSession")}</small></div><button type="button" onClick={() => setOpen(false)} aria-label={t("close")}><X /></button></header><p className="assistant-intro">{t("assistantIntro")}</p>{result && <div className="assistant-answer"><FileSearch size={18} /><div><p>{result.answer}</p><small>{(result.document_evidence?.length ?? 0) + (result.graph_evidence?.length ?? 0)} {t("evidenceMatches")}</small></div></div>}{error && <div className="login-error" role="alert">{error}</div>}<form onSubmit={submit}><label htmlFor="assistant-question">{t("askAssistant")}</label><textarea id="assistant-question" value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} placeholder="FIR_P_0049, station, Act or section"/><button type="submit" disabled={loading || question.trim().length < 4}>{loading ? "..." : <><Send size={16}/>{t("send")}</>}</button></form></motion.aside>}</AnimatePresence></>;
}
