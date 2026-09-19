import { useState, type FormEvent } from "react";
import { LockKeyhole, UserRound, X, Eye, EyeOff } from "lucide-react";
import { motion } from "motion/react";
import { useAuth } from "../auth/AuthContext";
import { LANGUAGE_OPTIONS, useLanguage, type Language } from "../i18n/LanguageContext";
import BrandLogo from "../components/BrandLogo";
import AmbientInvestigationBackground from "../components/motion-primitives/AmbientInvestigationBackground";
import { api } from "../api/client.ts";

export default function Login() {
 const { login } = useAuth();
 const {language,setLanguage,t}=useLanguage();
 const [username,setUsername]=useState("admin");
 const [password,setPassword]=useState("password123");
 const [showPassword, setShowPassword] = useState(false);
 const [notice,setNotice]=useState("");
 const [error,setError]=useState("");
 const [loading,setLoading]=useState(false);
 const [recover,setRecover]=useState(false);
 const [code,setCode]=useState("");
 const [replacement,setReplacement]=useState("");
 const [confirm,setConfirm]=useState("");
 async function submit(event:FormEvent) {
  event.preventDefault();setError("");setLoading(true);
  try { await login(username.trim(),password); }
  catch {setError(t("loginError"));} finally {setLoading(false);}
 }
 async function reset(event:FormEvent) {
  event.preventDefault();setError("");
  if(replacement!==confirm){setError(t("passwordMismatch"));return;}
  setLoading(true);
  try {await api.post("/auth/reset-password",{code:code.trim(),password:replacement});setRecover(false);setCode("");setReplacement("");setConfirm("");setPassword("");setNotice(t("resetSuccess"));}
  catch {setError(t("resetError"));} finally {setLoading(false);}
 }
 return <main className="login-page">
  <section className="login-intro"><AmbientInvestigationBackground /><div className="login-brand"><BrandLogo /><strong>ShadowNet</strong></div>
   <motion.h1 initial={{opacity:0,y:16}} animate={{opacity:1,y:0}}>{t("loginIntro")}</motion.h1><p>{t("loginBody")}</p>
   <div className="login-orbits" aria-hidden="true"><span/><span/><span/><i/><i/><i/></div>
  </section>
  <section className="login-panel"><div className="login-language"><label htmlFor="login-language">{t("languageTitle")}</label><select id="login-language" value={language} onChange={e=>setLanguage(e.target.value as Language)}>{LANGUAGE_OPTIONS.map(x=><option key={x.code} value={x.code}>{x.label}</option>)}</select></div>
   <motion.form onSubmit={submit} className="login-form" initial={{opacity:0,y:12}} animate={{opacity:1,y:0}}>
    <h2>{t("loginTitle")}</h2>
    <label htmlFor="username">{t("identifier")}</label><div className="login-field"><UserRound size={18}/><input id="username" autoComplete="username" value={username} onChange={e=>setUsername(e.target.value)} required minLength={3}/></div>
    <label htmlFor="password">{t("password")}</label><div className="login-field"><LockKeyhole size={18}/><input id="password" type={showPassword ? "text" : "password"} autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} required minLength={8}/><button type="button" onClick={() => setShowPassword(!showPassword)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", color: "inherit", padding: "0 4px", width: "auto", minHeight: "auto", margin: 0 }} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div>
    {error&&!recover&&<div className="login-error" role="alert">{error}</div>}{notice&&<div className="success-notice" role="status">{notice}</div>}
    <button type="submit" disabled={loading}>{loading?t("working"):t("signIn")}</button><button className="recovery-link" type="button" onClick={()=>{setError("");setRecover(true);}}>{t("accountRecovery")}</button>
   </motion.form>
  </section>
  {recover&&<div className="recovery-scrim" role="dialog" aria-modal="true" aria-labelledby="recovery-title"><form className="recovery-card" onSubmit={reset}><button className="tour-close" type="button" onClick={()=>{setRecover(false);setError("");}} aria-label={t("close")}><X/></button><h2 id="recovery-title">{t("recoveryTitle")}</h2><p>{t("recoveryBody")}</p>
   <label htmlFor="recovery-code">{t("recoveryCode")}</label><input autoFocus id="recovery-code" autoComplete="one-time-code" value={code} onChange={e=>setCode(e.target.value)} required minLength={20}/>
   <label htmlFor="new-password">{t("newPassword")}</label><input id="new-password" type="password" autoComplete="new-password" value={replacement} onChange={e=>setReplacement(e.target.value)} required minLength={15} maxLength={200}/>
   <label htmlFor="confirm-password">{t("confirmPassword")}</label><input id="confirm-password" type="password" autoComplete="new-password" value={confirm} onChange={e=>setConfirm(e.target.value)} required/>
   {error&&<p className="login-error" role="alert">{error}</p>}<button type="submit" disabled={loading}>{loading?t("working"):t("resetPassword")}</button>
  </form></div>}
 </main>;
}
