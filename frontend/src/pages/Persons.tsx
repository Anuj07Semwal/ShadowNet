import {useEffect,useState} from "react";
import {Link,useSearchParams} from "react-router-dom";
import {ArrowRight, UserRound} from "lucide-react";
import {getPersons} from "../api/persons";
import type {Person} from "../types/person";
import {useLanguage} from "../i18n/LanguageContext";
import {recordLabel} from "../utils/displayLabels";
export default function Persons(){
 const {t,language}=useLanguage();const [params,setParams]=useSearchParams();const search=params.get("search")??"";
 const [persons,setPersons]=useState<Person[]>([]);const [busy,setBusy]=useState(true);const [error,setError]=useState(false);const [retry,setRetry]=useState(0);
 useEffect(()=>{let active=true;getPersons(500).then(data=>{if(active){setPersons(data.persons);setError(false);}}).catch(()=>{if(active)setError(true);}).finally(()=>{if(active)setBusy(false);});return()=>{active=false;};},[retry]);
 const visible=persons.filter(p=>recordLabel(p.person_id,p.name,language).toLowerCase().includes(search.toLowerCase()));
 return <div className="workspace-page"><h1>{t("persons")}</h1><p>{t("nameHelp")}</p><label htmlFor="person-search">{t("search")}</label><input id="person-search" value={search} onChange={e=>setParams({search:e.target.value},{replace:true})}/>
 {busy&&<p role="status">{t("working")}</p>}{error&&<div role="alert">{t("backendReason")} <button onClick={()=>setRetry(n=>n+1)}>{t("retry")}</button></div>}
 <div className="person-grid">{visible.map(p=><article className="person-card" key={p.person_id}><Link className="person-card-main" to={`/persons/${encodeURIComponent(p.person_id)}`} aria-label={`View profile for ${recordLabel(p.person_id,p.name,language)}`}><span className="person-card-icon"><UserRound size={22}/></span><span className="person-card-copy"><strong>{recordLabel(p.person_id,p.name,language)}</strong><small>Person ID: {p.person_id}</small><span>{p.degree??0} {t("connections")}</span></span><ArrowRight className="person-card-arrow" size={19}/></Link><Link className="secondary-action" to={`/network?person=${encodeURIComponent(p.person_id)}`}>{t("generate")}</Link></article>)}</div>
 {!busy&&!error&&!visible.length&&<p>{t("noResults")}</p>}</div>;
}
