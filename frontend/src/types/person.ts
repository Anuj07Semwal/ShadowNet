export interface Person {
  person_id: string;
  name: string | null;
  source?: string | null;
  source_role?: string | null;
  confidence?: number | null;

  degree?: number | null;
  degree_centrality?: number | null;
  betweenness?: number | null;
  pagerank?: number | null;

  community_id?: number | null;
  community_size?: number | null;
}

export interface PersonListResponse {
  count: number;
  persons: Person[];
}

export interface NetworkConnection {
  id: string;
  name: string | null;
  type: string[];
  relationship: string;
}

export interface PersonNetwork {
  person_id: string;
  name: string | null;

  degree: number | null;
  degree_centrality: number | null;
  betweenness: number | null;
  pagerank: number | null;
  community: number | null;
  community_size: number | null;

  connections: NetworkConnection[];
}

export interface PersonAnomaly {
  transaction_id: string;
  amount: number | null;
  timestamp: string | null;
  anomaly_score: number | null;
  is_anomaly: boolean;
}

