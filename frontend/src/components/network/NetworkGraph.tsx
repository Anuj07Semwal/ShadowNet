import {useMemo,useState} from "react";
import {ReactFlow,Background,Controls,type Node,type Edge} from "reactflow";
import "reactflow/dist/style.css";
import type {PersonNetwork} from "../../types/person";
import {useLanguage} from "../../i18n/LanguageContext";
import {recordLabel} from "../../utils/displayLabels";
import {getCaseEvidence,type CaseEvidenceItem} from "../../api/cases";
export default function NetworkGraph({network}:{network:PersonNetwork}){
 const {t,language}=useLanguage();const [count,setCount]=useState(12);const [evidence,setEvidence]=useState<CaseEvidenceItem[]>([]);const [selected,setSelected]=useState("");const [busy,setBusy]=useState(false);const [error,setError]=useState(false);
 const graph=useMemo(()=>{
  const nodes:Node[]=[{id:network.person_id,position:{x:0,y:0},data:{label:recordLabel(network.person_id,network.name,language)},style:{background:"var(--color-primary)",color:"var(--color-primary-foreground)",width:180,padding:14,borderRadius:8}}];
  const edges:Edge[]=[];
  network.connections.slice(0,count).forEach((c,i)=>{const angle=2*Math.PI*i/Math.max(1,Math.min(count,network.connections.length));const radius=Math.max(270,Math.min(count,network.connections.length)*25);
   nodes.push({id:c.id,position:{x:Math.cos(angle)*radius,y:Math.sin(angle)*radius},data:{label:recordLabel(c.id,c.name,language)},style:{background:"var(--color-card)",color:"var(--color-foreground)",border:"2px solid #ba941a",width:160,padding:12,borderRadius:8}});
   edges.push({id:"link-"+i,source:network.person_id,target:c.id,label:t("mentioned"),style:{stroke:"#967310"},labelStyle:{fill:"var(--color-foreground)"},labelBgStyle:{fill:"var(--color-card)"}});
  });return {nodes,edges};
 },[network,count,language,t]);
 async function inspect(id:string){if(id===network.person_id)return;setSelected(id);setBusy(true);setError(false);setEvidence([]);try{setEvidence((await getCaseEvidence(id)).evidence);}catch{setError(true);}finally{setBusy(false);}}
 return <div className="network-graph-shell"><div className="graph-toolbar"><p>{t("focusPerson")} → {t("caseRecord")} · {t("viewEvidence")}</p><label>{t("visibleLinks")} <select value={count} onChange={e=>setCount(Number(e.target.value))}>{[12,24,40].map(n=><option key={n}>{n}</option>)}</select></label></div>
 <div className="graph-canvas"><ReactFlow key={network.person_id+count+language} nodes={graph.nodes} edges={graph.edges} fitView minZoom={.15} nodesConnectable={false} onNodeClick={(_,node)=>void inspect(node.id)} proOptions={{hideAttribution:true}}><Background/><Controls showInteractive={false}/></ReactFlow></div>
 {!network.connections.length&&<p>{t("noResults")}</p>}
 {selected&&<section className="graph-source" aria-live="polite"><h3>{recordLabel(selected,null,language)}</h3>{busy?<p>{t("working")}</p>:error?<p role="alert">{t("error")}</p>:<><small>{t("sourceOriginal")}</small>{evidence.map((e,i)=><article key={i}><strong>{e.title}</strong><p>{e.summary}</p></article>)}</>}</section>}</div>;
}
