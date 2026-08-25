import api from './api';

let inMemoryToken = '';

export function getAccessToken(): string {
  if (inMemoryToken) {
    return inMemoryToken;
  }
  
  if (typeof window !== 'undefined') {
    const match = document.cookie.match(/(^| )access_token=([^;]+)/);
    if (match) {
      inMemoryToken = match[2];
      return inMemoryToken;
    }
  }
  return '';
}

export function setAccessToken(token: string) {
  inMemoryToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      document.cookie = `access_token=${token}; path=/; max-age=3600; SameSite=Strict`;
    } else {
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  }
}

export async function loginUser(email: string, password: string): Promise<any> {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const response = await api.post('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  const { access_token } = response.data;
  setAccessToken(access_token);
  return response.data;
}

export async function registerUser(email: string, password: string, roleName: string = 'Planner'): Promise<any> {
  const response = await api.post('/auth/register', {
    email,
    password,
    role_name: roleName,
  });
  return response.data;
}

export async function getMe(): Promise<any> {
  const response = await api.get('/auth/me');
  return response.data;
}

export function logout() {
  setAccessToken('');
}
