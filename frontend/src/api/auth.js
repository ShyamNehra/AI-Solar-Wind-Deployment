import apiClient from './client';

/**
 * Auth API Service — Module 1
 * Handles all authentication, registration, and user management API calls.
 */

// ── Public Auth Endpoints ──────────────────────────────────

export async function loginUser(usernameOrEmail, password, organizationId) {
  const res = await apiClient.post('/auth/login', {
    username_or_email: usernameOrEmail,
    password,
    organization_id: organizationId || undefined
  });
  return res.data;
}

export async function registerUser(payload) {
  const res = await apiClient.post('/auth/register', payload);
  return res.data;
}

export async function checkWorkspaceAvailability(workspaceCode) {
  const res = await apiClient.get('/auth/check-workspace', {
    params: { workspace_code: workspaceCode }
  });
  return res.data;
}


// ── Authenticated User Endpoints ───────────────────────────

export async function fetchMe() {
  const res = await apiClient.get('/auth/me');
  return res.data;
}

export async function updateProfile(payload) {
  const res = await apiClient.put('/auth/me', payload);
  return res.data;
}


// ── Admin-Only Endpoints ───────────────────────────────────

export async function fetchAllUsers() {
  const res = await apiClient.get('/auth/users');
  return res.data;
}

export async function changeUserRole(userId, role) {
  const res = await apiClient.put(`/auth/users/${userId}/role`, { role });
  return res.data;
}

export async function toggleUserActive(userId) {
  const res = await apiClient.delete(`/auth/users/${userId}`);
  return res.data;
}


// ── Token Helpers ──────────────────────────────────────────

export function saveToken(token) {
  localStorage.setItem('access_token', token);
}

export function getToken() {
  return localStorage.getItem('access_token');
}

export function clearToken() {
  localStorage.removeItem('access_token');
}
