import { lazy, Suspense, useEffect, useState } from "react";
import { ArrowRight, Network } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { getPersons,getPersonNetwork } from "../api/persons";
import type {Person,PersonNetwork} from "../types/person";
import {useLanguage} from "../i18n/LanguageContext";
import {recordLabel} from "../utils/displayLabels";
const NetworkGraph=lazy(()=>import("../components/network/NetworkGraph"));
export default function NetworkExplorer(){
 const {t,language}=useLanguage();const [params]=useSearchParams();
 const [persons,setPersons]=useState<Person[]>([]);const [selected,setSelected]=useState(params.get("person")??"");
 const [filter,setFilter]=useState("");const [network,setNetwork]=useState<PersonNetwork|null>(null);const [busy,setBusy]=useState(false);const [error,setError]=useState(false);const [retry,setRetry]=useState(0);
 useEffect(()=>{let active=true;getPersons(500).then(data=>{if(active){setPersons(data.persons);setError(false);}}).catch(()=>{if(active)setError(true);});return()=>{active=false;};},[retry]);
 async function generate(){if(!selected)return;setBusy(true);setError(false);setNetwork(null);try{setNetwork(await getPersonNetwork(selected));}catch{setError(true);}finally{setBusy(false);}}
 const visible=persons.filter(p=>recordLabel(p.person_id,p.name,language).toLowerCase().includes(filter.toLowerCase()));
 return <div className="workspace-page"><h1>{t("network")}</h1><p>{t("graphHelp")}</p><small>{t("sourceNote")}</small>
  <section className="settings-card graph-generator"><label htmlFor="record-filter">{t("search")}</label><input id="record-filter" value={filter} onChange={e=>setFilter(e.target.value)}/>
  <label htmlFor="person-select">{t("selectPerson")}</label><select id="person-select" value={selected} onChange={e=>{setSelected(e.target.value);setNetwork(null);}}><option value="">{t("selectPerson")}</option>{visible.map(p=><option key={p.person_id} value={p.person_id}>{recordLabel(p.person_id,p.name,language)} · {p.degree??0} {t("connections")}</option>)}</select>
  <button className="primary-action" onClick={()=>void generate()} disabled={!selected||busy}><Network size={18}/>{busy?t("working"):t("generate")}</button></section>
  {error&&<div className="login-error" role="alert">{t("backendReason")} <button onClick={()=>setRetry(n=>n+1)}>{t("retry")}</button></div>}
    {network&&<section className="data-panel"><div className="panel-heading"><div><p className="eyebrow">Selected person</p><h2>{recordLabel(network.person_id,network.name,language)}</h2><small>Person ID: {network.person_id}</small></div><Link className="secondary-action" to={`/persons/${encodeURIComponent(network.person_id)}`}>View Profile <ArrowRight size={16}/></Link></div><Suspense fallback={<p role="status">{t("working")}</p>}><NetworkGraph key={network.person_id} network={network}/></Suspense></section>}
 </div>;
}
