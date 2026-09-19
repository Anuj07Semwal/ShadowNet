import { api } from "./client.ts";

export interface NetworkStatsResponse {
  total_nodes: number;
  entities?: Record<string, number>;
}

export interface NetworkPerson {
  person_id: string;
  name?: string;
  degree?: number;
  degree_centrality?: number;
  betweenness?: number;
  pagerank?: number;
  community_id?: string | number | null;
}

export interface TopPersonsResponse {
  metric: string;
  persons?: NetworkPerson[];
}

export async function getNetworkStats(): Promise<NetworkStatsResponse> {
  const response = await api.get<NetworkStatsResponse>("/network/stats");
  return response.data;
}

export async function getTopPersons(
  metric = "pagerank",
  limit = 10
): Promise<TopPersonsResponse> {
  const response = await api.get<TopPersonsResponse>("/network/top-persons", {
    params: {
      metric,
      limit,
    },
  });

  return response.data;
}
