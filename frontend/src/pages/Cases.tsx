import {useEffect,useState} from "react";
import {useSearchParams} from "react-router-dom";
import {getCases,getCaseEvidence,type CaseItem,type CaseEvidenceItem} from "../api/cases";
import {useLanguage} from "../i18n/LanguageContext";
import {recordLabel} from "../utils/displayLabels";
export default function Cases(){
 const {t,language}=useLanguage();const [params]=useSearchParams();const [cases,setCases]=useState<CaseItem[]>([]);const [selected,setSelected]=useState(params.get("case")??"");const [evidence,setEvidence]=useState<CaseEvidenceItem[]>([]);const [error,setError]=useState(false);const [busy,setBusy]=useState(true);
 useEffect(()=>{getCases().then(x=>setCases(x.cases)).catch(()=>setError(true)).finally(()=>setBusy(false));},[]);
 useEffect(()=>{if(!selected)return;let active=true;getCaseEvidence(selected).then(x=>{if(active)setEvidence(x.evidence);}).catch(()=>{if(active)setError(true);}).finally(()=>{if(active)setBusy(false);});return()=>{active=false;};},[selected]);
 return <div className="workspace-page"><h1>{t("cases")}</h1><p>{t("sourceNote")}</p>{error&&<p role="alert">{t("error")}</p>}
 <div className="case-layout"><div className="case-list">{cases.map(item=><button className={selected===item.id?"selected":""} key={item.id} onClick={()=>{setBusy(true);setError(false);setEvidence([]);setSelected(item.id);}}><strong>{recordLabel(item.id,item.name,language)}</strong><span>{item.title}</span><small>{item.owner} · {item.evidence_count} {t("evidenceMatches")}</small></button>)}</div>
 <section className="settings-card">{busy?<p role="status">{t("working")}</p>:selected?<><h2>{recordLabel(selected,cases.find(item=>item.id===selected)?.name,language)}</h2><small>{t("sourceOriginal")}</small>{evidence.map((e,i)=><article className="evidence-result" key={i}><strong>{e.entity_name||e.title}</strong><p>{e.summary}</p></article>)}{!evidence.length&&!error&&<p>{t("noEvidence")}</p>}</>:<p>{t("selectCase")}</p>}</section></div></div>;
}
