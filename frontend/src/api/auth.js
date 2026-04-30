import { apiFetch, setToken, setRefreshToken, clearTokens } from './client.js';

export async function login(email, password) {
  const data = await apiFetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  setRefreshToken(data.refresh_token);
  return data.user;
}

export async function register(email, password, fullName) {
  const data = await apiFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  setToken(data.access_token);
  setRefreshToken(data.refresh_token);
  return data.user;
}

export async function getProfile() {
  return apiFetch('/api/auth/me');
}

export async function logout() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    try {
      await apiFetch('/api/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch { /* ignore */ }
  }
  clearTokens();
}
