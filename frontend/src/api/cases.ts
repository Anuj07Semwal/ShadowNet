import { api } from "./client.ts";

export interface CaseItem {
  id: string;
  name: string;
  title: string;
  status: string;
  priority: string;
  risk_score: number;
  evidence_count: number;
  owner: string;
}

export interface CaseEvidenceItem {
  type: string;
  title: string;
  entity_id?: string | null;
  entity_name?: string | null;
  summary?: string;
  confidence?: number;
}

export async function getCases(): Promise<{ cases: CaseItem[] }> {
  const response = await api.get<{ cases: CaseItem[] }>("/cases");
  return response.data;
}

export async function getCaseEvidence(caseId: string): Promise<{ case_id: string; evidence: CaseEvidenceItem[] }> {
  const response = await api.get<{ case_id: string; evidence: CaseEvidenceItem[] }>(`/cases/${caseId}/evidence`);
  return response.data;
}
