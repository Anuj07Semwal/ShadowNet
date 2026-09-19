import { api } from "./client.ts";

export interface WorkspaceInvestigation {
  id: string;
  created_at: string;
  question: string;
  matching_records: number;
  summary?: string;
}

export interface WorkspaceUpload {
  id: string;
  created_at: string;
  filename: string;
  size_bytes: number;
  status: string;
}

export interface WorkspaceDashboard {
  username: string;
  investigation_count: number;
  upload_count: number;
  evidence_match_count: number;
  recent_investigations: WorkspaceInvestigation[];
  recent_uploads: WorkspaceUpload[];
}

export async function getWorkspaceDashboard() {
  return (await api.get<WorkspaceDashboard>("/workspace/dashboard")).data;
}

export async function deleteWorkspaceInvestigation(id: string) {
  return (await api.delete<{ status: string; id: string }>(`/workspace/investigations/${encodeURIComponent(id)}`)).data;
}
