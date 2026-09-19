import {useState,useRef} from "react";
import {Link} from "react-router-dom";
import {motion} from "motion/react";
import {Send} from "lucide-react";
import {api} from "../api/client.ts";
import {useLanguage} from "../i18n/LanguageContext";
import {recordLabel,readableText} from "../utils/displayLabels";
interface Result{answer:string;graph_evidence:{data?:string[];persons?:string[];station?:string}[];document_evidence:{title?:string;summary?:string;content?:string}[]}
interface Turn{question:string;result?:Result;error?:boolean}
export default function Investigation(){
 const {t,language}=useLanguage();const [question,setQuestion]=useState("");const [turns,setTurns]=useState<Turn[]>([]);const [busy,setBusy]=useState(false);const lock=useRef(false);
 async function send(){const text=question.trim();if(text.length<4||lock.current)return;lock.current=true;setBusy(true);setQuestion("");setTurns(old=>[...old,{question:text}]);
 try{const {data}=await api.post<Result>("/graph-rag/investigate",{question:text,language},{timeout:30000});setTurns(old=>old.map((x,i)=>i===old.length-1?{...x,result:data}:x));}catch{setTurns(old=>old.map((x,i)=>i===old.length-1?{...x,error:true}:x));}finally{lock.current=false;setBusy(false);}}
 return <div className="workspace-page conversation-page"><h1>{t("investigation")}</h1><p>{t("questionHelp")}</p><small>{t("sourceNote")}</small>
 <div className="prompt-grid">{["promptPeople","promptStations","promptArms"].map(k=><button type="button" key={k} disabled={busy} onClick={()=>setQuestion(t(k))}>{t(k)}</button>)}</div>
 <div className="conversation" aria-live="polite">{turns.map((turn,i)=><motion.section key={i} initial={{opacity:0,y:10}} animate={{opacity:1,y:0}}><p className="question-bubble">{readableText(turn.question,language)}</p>
 {turn.error?<p className="login-error" role="alert">{t("error")}</p>:turn.result?<article className="answer-card"><h2>{t("analysis")}</h2><p>{readableText(turn.result.answer,language)}</p><h3>{t("graphEvidence")}</h3>
 {turn.result.graph_evidence?.length?turn.result.graph_evidence.map((e,j)=><div className="evidence-result" key={j}><Link to={`/cases?case=${encodeURIComponent(e.data?.[0]??"")}`}>{recordLabel(e.data?.[0]??"",null,language)}</Link><p>{e.station}</p><div className="evidence-people">{(e.persons??[]).slice(0,6).map(id=><Link key={id} to={`/network?person=${encodeURIComponent(id)}`}>{recordLabel(id,null,language)} · {t("generate")}</Link>)}</div></div>):<p>{t("noEvidence")}</p>}
 <h3>{t("documentEvidence")}</h3><small>{t("sourceOriginal")}</small>{turn.result.document_evidence?.map((e,j)=><div key={j}><strong>{readableText(e.title??"",language)}</strong><p>{e.content??e.summary}</p></div>)}</article>:<p role="status">{t("working")}</p>}
 </motion.section>)}</div>
 <form className="question-composer" onSubmit={e=>{e.preventDefault();void send();}}><label htmlFor="question">{t("questionPlaceholder")}</label><textarea id="question" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={2000} rows={3} required minLength={4}/><button className="primary-action" disabled={busy||question.trim().length<4}><Send size={18}/>{busy?t("working"):t("send")}</button></form>
 </div>;
}
