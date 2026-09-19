import {useEffect,useState,type FormEvent} from "react";
import {PlayCircle,Trash2} from "lucide-react";
import {getWorkspaceDashboard,deleteWorkspaceInvestigation,type WorkspaceDashboard} from "../api/workspace.ts";
import {LANGUAGE_OPTIONS,useLanguage,type Language} from "../i18n/LanguageContext";
import {usePreferences,type ThemeChoice} from "../preferences/PreferencesContext";
import {useAuth} from "../auth/AuthContext";
import {api} from "../api/client.ts";
import {readableText} from "../utils/displayLabels";
export default function Settings(){
 const {language,setLanguage,t}=useLanguage();const {theme,setTheme}=usePreferences();const {session,logout}=useAuth();
 const [workspace,setWorkspace]=useState<WorkspaceDashboard|null>(null);const [confirmId,setConfirmId]=useState("");const [notice,setNotice]=useState("");const [error,setError]=useState(false);const [busy,setBusy]=useState(false);
 const [current,setCurrent]=useState("");const [replacement,setReplacement]=useState("");const [confirm,setConfirm]=useState("");
 useEffect(()=>{getWorkspaceDashboard().then(setWorkspace).catch(()=>setError(true));},[]);
 async function remove(id:string){setBusy(true);setError(false);try{await deleteWorkspaceInvestigation(id);setWorkspace(x=>x?{...x,recent_investigations:x.recent_investigations.filter(i=>i.id!==id)}:x);setConfirmId("");setNotice(t("deleted"));}catch{setError(true);}finally{setBusy(false);}}
 async function change(e:FormEvent){e.preventDefault();setNotice("");if(replacement!==confirm){setNotice(t("passwordMismatch"));return;}setBusy(true);setError(false);try{await api.post("/auth/change-password",{current_password:current,password:replacement});await logout();}catch{setError(true);}finally{setBusy(false);}}
 return <div className="settings-page workspace-page"><h1>{t("settingsTitle")}</h1>{error&&<p className="login-error" role="alert">{t("error")}</p>}{notice&&<p className="success-notice" role="status">{notice}</p>}
 <section className="settings-card"><h2>{t("appearance")}</h2><p>{t("appearanceHelp")}</p><div className="segmented-control">{(["light","dark","system"] as ThemeChoice[]).map(v=><button className={theme===v?"selected":""} type="button" onClick={()=>setTheme(v)} key={v}>{t(v)}</button>)}</div></section>
 <section className="settings-card"><label htmlFor="settings-language">{t("languageTitle")}</label><select id="settings-language" value={language} onChange={e=>setLanguage(e.target.value as Language)}>{LANGUAGE_OPTIONS.map(x=><option key={x.code} value={x.code}>{x.label}</option>)}</select></section>
 <section className="settings-card"><h2>{t("tutorial")}</h2><button className="secondary-action" onClick={()=>window.dispatchEvent(new Event("shadownet:replay-tutorial"))}><PlayCircle size={18}/>{t("replayTutorial")}</button></section>
 <section className="settings-card"><h2>{t("passwordSecurity")}</h2><p>{t("passwordReminderHelp")}</p><p>{t("passwordReminder")}: {Math.max(0,(session?.password_review_days??45)-(session?.password_age_days??0))} {t("days")}</p>
 <form className="password-form" onSubmit={e=>void change(e)}><label htmlFor="current-password">{t("password")}</label><input id="current-password" type="password" autoComplete="current-password" required value={current} onChange={e=>setCurrent(e.target.value)}/>
 <label htmlFor="new-password">{t("newPassword")}</label><input id="new-password" type="password" autoComplete="new-password" minLength={15} maxLength={200} required value={replacement} onChange={e=>setReplacement(e.target.value)}/>
 <label htmlFor="confirm-password">{t("confirmPassword")}</label><input id="confirm-password" type="password" autoComplete="new-password" required value={confirm} onChange={e=>setConfirm(e.target.value)}/><button className="primary-action" disabled={busy}>{t("changePassword")}</button></form></section>
 <section className="settings-card danger-zone"><h2>{t("deleteHistory")}</h2><p>{t("deleteHistoryHelp")}</p><div className="settings-history">{workspace?.recent_investigations.map(item=><article key={item.id}><strong>{readableText(item.question,language)}</strong>{confirmId===item.id?<div className="confirm-actions"><span>{t("confirmDelete")}</span><button disabled={busy} onClick={()=>void remove(item.id)}>{t("delete")}</button><button onClick={()=>setConfirmId("")}>{t("cancel")}</button></div>:<button className="delete-button" onClick={()=>setConfirmId(item.id)}><Trash2 size={16}/>{t("delete")}</button>}</article>)}</div>{workspace&&!workspace.recent_investigations.length&&<p>{t("noActivity")}</p>}</section>
 </div>;
}
