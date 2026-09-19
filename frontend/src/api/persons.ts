import { api } from "./client.ts";

import type {
  Person,
  PersonListResponse,
  PersonNetwork,
} from "../types/person";

export interface ProfileEntity {
  id: string;
  name: string | null;
  type: string;
  properties: Record<string, unknown>;
}

export interface ProfileRelationship extends ProfileEntity {
  relationship: string;
  direction?: string | null;
  confidence?: number | null;
}

export interface PersonProfile {
  id: string;
  name: string;
  basic: Record<string, unknown>;
  locations: ProfileEntity[];
  vehicles: ProfileEntity[];
  organizations: ProfileEntity[];
  phones: ProfileEntity[];
  emails: Array<Record<string, unknown>>;
  accounts: ProfileEntity[];
  transactions: Array<Record<string, unknown>>;
  relationships: ProfileRelationship[];
  risk: PersonRiskProfile;
  graph: {
    nodes: Array<{ id: string; type: string; label: string }>;
    edges: Array<{ source: string; target: string; relationship: string }>;
  };
}

export interface PersonRiskProfile {
  score: number;
  band: "high" | "medium" | "low";
  method: string;
  factors: Array<{ name: string; value: number; unit: string }>;
  anomalies: Array<{
    id: string;
    type: string;
    severity: "high" | "medium" | "low";
    date: string | null;
    transaction_id: string;
    amount: number;
    channel?: string | null;
    score: number;
    reason?: string | null;
  }>;
  associations: Array<{ id: string; type: string; label: string; source: string }>;
  cases: Array<{ id: string; source: string; status: string; date?: string; title: string; station?: string; summary?: string; confidence: number }>;
  history: Array<{ date: string; score: number }>;
}


export async function getPersons(
  limit = 100
): Promise<PersonListResponse> {

  const response = await api.get<PersonListResponse>(
    `/persons?limit=${limit}`
  );

  return response.data;
}


export async function getPerson(
  personId: string
): Promise<Person> {

  const response = await api.get<Person>(
    `/persons/${encodeURIComponent(personId)}`
  );

  return response.data;
}

export async function getPersonProfile(personId: string): Promise<PersonProfile> {
  const response = await api.get<PersonProfile>(
    `/persons/${encodeURIComponent(personId)}/profile`
  );
  return response.data;
}


export async function getPersonNetwork(
  personId: string
): Promise<PersonNetwork> {

  const response = await api.get<PersonNetwork>(
    `/persons/${encodeURIComponent(personId)}/network`
  );

  return response.data;
}


