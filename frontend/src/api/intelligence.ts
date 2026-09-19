import { api } from "./client.ts";

export interface NetworkIntelSummary {
  network: {
    total_nodes: number;
    relationships: number;
    communities: number;
    graph_density: number;
  };
  risk: {
    overall_score: number;
    anomaly_count: number;
    high_priority_entities: number;
  };
  entities: Record<string, number>;
  status: string;
}

export async function getIntelligenceSummary(): Promise<NetworkIntelSummary> {
  const response = await api.get<NetworkIntelSummary>("/intelligence/summary");
  return response.data;
}

export async function getLiveGraphStats(): Promise<{
  graph_name: string;
  node_count: number;
  relationship_count: number;
  community_count: number;
  top_risk_areas: string[];
}> {
  const response = await api.get("/intelligence/network");
  return response.data;
}
