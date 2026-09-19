import { api } from "./client";

export async function getPersons(limit = 100) {
  const response = await api.get(`/persons?limit=${limit}`);
  return response.data;
}

export async function getPerson(personId) {
  const response = await api.get(`/persons/${encodeURIComponent(personId)}`);
  return response.data;
}

export async function getPersonProfile(personId) {
  const response = await api.get(`/persons/${encodeURIComponent(personId)}/profile`);
  return response.data;
}

export async function getPersonNetwork(personId) {
  const response = await api.get(`/persons/${encodeURIComponent(personId)}/network`);
  return response.data;
}

export async function getPersonConnections(personId) {
  const response = await api.get(`/persons/${encodeURIComponent(personId)}/connections`);
  return response.data;
}

export async function getPersonRelationships(personId) {
  const response = await api.get(`/persons/${encodeURIComponent(personId)}/relationships`);
  return response.data;
}