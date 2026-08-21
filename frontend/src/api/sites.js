import apiClient from './client';

export async function fetchSavedSites(orgId) {
  const response = await apiClient.get(`/sites/saved?organization_id=${orgId}`);
  return response.data;
}

export async function saveSite(payload) {
  const response = await apiClient.post('/sites/saved', payload);
  return response.data;
}

export async function deleteSavedSite(siteId, orgId) {
  const response = await apiClient.delete(`/sites/saved/${siteId}?organization_id=${orgId}`);
  return response.data;
}

export async function fetchRecentSites(orgId) {
  const response = await apiClient.get(`/sites/recent?organization_id=${orgId}`);
  return response.data;
}

export async function saveRecentSite(payload) {
  const response = await apiClient.post('/sites/recent', payload);
  return response.data;
}
