import api from './api';

export async function getNotifications(): Promise<any[]> {
  const response = await api.get('/notifications');
  return response.data;
}

export async function markNotificationAsRead(notificationId: number): Promise<any> {
  const response = await api.post(`/notifications/${notificationId}/read`);
  return response.data;
}
