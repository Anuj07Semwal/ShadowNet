import { useMemo, useState } from "react";
import { Building2, CarFront, CircleDot, CreditCard, Mail, MapPin, Phone, UserRound } from "lucide-react";
import { Handle, Position, ReactFlow, Background, Controls, type Edge, type Node, type NodeProps } from "reactflow";
import "reactflow/dist/style.css";
import type { PersonProfile } from "../../api/persons";

interface ProfileGraphProps {
  profile: PersonProfile;
  onPersonSelect: (personId: string) => void;
}

const typeOptions = ["person", "organization", "vehicle", "location", "phone", "account", "transaction"];

const entityIcons = {
  person: UserRound,
  organization: Building2,
  vehicle: CarFront,
  location: MapPin,
  phone: Phone,
  account: CreditCard,
  transaction: CreditCard,
  email: Mail,
};

type EntityNodeData = { label: string; type: string; selected: boolean; onActivate: () => void };

function EntityNode({ data }: NodeProps<EntityNodeData>) {
  const Icon = entityIcons[data.type as keyof typeof entityIcons] ?? CircleDot;
  return <div className={`profile-graph-node ${data.selected ? "profile-graph-node-selected" : ""}`} role="button" tabIndex={0} aria-label={`Open ${data.type} ${data.label}`} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); data.onActivate(); } }} onClick={data.onActivate}>
    <Handle type="target" position={Position.Top} />
    <Icon size={17} aria-hidden="true" />
    <span><strong>{data.label}</strong><small>{data.selected ? "Selected person" : data.type}</small></span>
    <Handle type="source" position={Position.Bottom} />
  </div>;
}

const nodeTypes = { entity: EntityNode };

export default function ProfileGraph({ profile, onPersonSelect }: ProfileGraphProps) {
  const [entityType, setEntityType] = useState("all");
  const [relationship, setRelationship] = useState("all");
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState(true);
  const [selected, setSelected] = useState<PersonProfile["graph"]["nodes"][number] | null>(null);

  const relationships = useMemo(
    () => Array.from(new Set(profile.graph.edges.map((edge) => edge.relationship))).sort(),
    [profile.graph.edges],
  );

  const visible = useMemo(() => {
    const query = search.trim().toLowerCase();
    const nodes = new Map(profile.graph.nodes.map((node) => [node.id, node]));
    const allowed = new Set<string>([profile.id]);
    profile.graph.nodes.forEach((node) => {
      const matchesType = entityType === "all" || node.type === entityType;
      const matchesSearch = !query || `${node.label} ${node.id}`.toLowerCase().includes(query);
      if (matchesType && matchesSearch) allowed.add(node.id);
    });
    const edges = profile.graph.edges.filter((edge) => {
      const matchesRelationship = relationship === "all" || edge.relationship === relationship;
      return matchesRelationship && allowed.has(edge.source) && allowed.has(edge.target);
    });
    if (!expanded) {
      const limited = new Set([profile.id, ...edges.slice(0, 12).flatMap((edge) => [edge.source, edge.target])]);
      return { nodes: [...limited].map((id) => nodes.get(id)).filter(Boolean), edges: edges.filter((edge) => limited.has(edge.source) && limited.has(edge.target)) };
    }
    return { nodes: [...allowed].map((id) => nodes.get(id)).filter(Boolean), edges };
  }, [entityType, expanded, profile.graph.edges, profile.graph.nodes, profile.id, relationship, search]);

  const graphNodes: Node<EntityNodeData>[] = visible.nodes.map((node, index) => ({
    id: node!.id,
    type: "entity",
    position: node!.id === profile.id ? { x: 0, y: 0 } : {
      x: Math.cos((index * 2 * Math.PI) / Math.max(1, visible.nodes.length - 1)) * 340,
      y: Math.sin((index * 2 * Math.PI) / Math.max(1, visible.nodes.length - 1)) * 230,
    },
    data: { label: node!.label, type: node!.type, selected: node!.id === profile.id, onActivate: () => selectNode(node!.id) },
  }));

  const graphEdges: Edge[] = visible.edges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${edge.relationship}-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.relationship,
    animated: edge.relationship === "CALLED" || edge.relationship === "EMAILED",
    labelStyle: { fill: "var(--color-foreground)", fontSize: 11 },
    labelBgStyle: { fill: "var(--color-card)" },
  }));

  function selectNode(nodeId: string) {
    const node = profile.graph.nodes.find((item) => item.id === nodeId);
    if (!node) return;
    setSelected(node);
    if (node.type === "person" && node.id !== profile.id) onPersonSelect(node.id);
  }

  const selectedDetails = selected ? [
    ...profile.phones,
    ...profile.vehicles,
    ...profile.locations,
    ...profile.organizations,
    ...profile.accounts,
  ].find((item) => item.id === selected.id) : null;
  const selectedTransaction = selected?.type === "transaction"
    ? profile.transactions.find((item) => item.transaction_id === selected.id)
    : null;

  return <section className="data-panel profile-graph-panel" id="relationship-graph">
    <div className="panel-heading"><div><h2>Relationship Graph</h2><p>Click a person or entity to view its details. The highlighted node is the selected person.</p><small>{visible.nodes.length} entities · {visible.edges.length} relationships</small></div><button type="button" onClick={() => setExpanded((value) => !value)}>{expanded ? "Collapse" : "Expand"}</button></div>
    <div className="profile-graph-filters">
      <label>Search<input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Name or ID" /></label>
      <label>Entity type<select value={entityType} onChange={(event) => setEntityType(event.target.value)}><option value="all">All types</option>{typeOptions.map((type) => <option key={type} value={type}>{type}</option>)}</select></label>
      <label>Relationship<select value={relationship} onChange={(event) => setRelationship(event.target.value)}><option value="all">All relationships</option>{relationships.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
    </div>
    <div className="profile-graph-canvas"><ReactFlow nodes={graphNodes} edges={graphEdges} nodeTypes={nodeTypes} fitView minZoom={0.15} nodesConnectable={false} onNodeClick={(_, node) => selectNode(node.id)} proOptions={{ hideAttribution: true }}><Background /><Controls showInteractive={false} /></ReactFlow></div>
    {selected && <aside className="profile-graph-inspector"><strong>{selected.label}</strong><span>{selected.type} · {selected.id}</span>{selectedDetails && Object.entries(selectedDetails.properties).slice(0, 6).map(([key, value]) => <span key={key}>{key.replaceAll("_", " ")}: {String(value)}</span>)}{selectedTransaction && Object.entries(selectedTransaction).slice(1, 6).map(([key, value]) => <span key={key}>{key.replaceAll("_", " ")}: {String(value)}</span>)}{selected.type === "person" && <button type="button" onClick={() => onPersonSelect(selected.id)}>Open profile</button>}</aside>}
  </section>;
}
