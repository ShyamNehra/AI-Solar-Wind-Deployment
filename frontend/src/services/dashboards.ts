import api from './api';

export async function getPlannerDashboard(projectId: number): Promise<any> {
  const response = await api.get(`/dashboards/planner/${projectId}`);
  return response.data;
}

export async function getGisAnalystDashboard(projectId: number): Promise<any> {
  const response = await api.get(`/dashboards/gis-analyst/${projectId}`);
  return response.data;
}

export async function getProjectManagerDashboard(projectId: number): Promise<any> {
  const response = await api.get(`/dashboards/project-manager/${projectId}`);
  return response.data;
}

export async function getAdminDashboard(): Promise<any> {
  const response = await api.get('/dashboards/admin');
  return response.data;
}

export async function getAdminDataSources(): Promise<any> {
  const response = await api.get('/admin/data-sources');
  return response.data;
}

export async function getAdminUsers(): Promise<any> {
  const response = await api.get('/admin/users');
  return response.data;
}

export async function getPlatformAnalytics(): Promise<any> {
  const response = await api.get('/admin/platform-analytics');
  return response.data;
}
