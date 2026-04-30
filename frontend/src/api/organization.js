// api/organization.js
import { apiFetch } from './client.js';

/** Get current user's organization profile. Resolves 404 as null (no profile yet). */
export async function getOrgProfile() {
  try {
    return await apiFetch('/api/organization');
  } catch (err) {
    if (err.status === 404) return null;
    throw err;
  }
}

/** Create or update the current user's organization profile. */
export async function upsertOrgProfile(data) {
  return apiFetch('/api/organization', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/** Delete the current user's organization profile. */
export async function deleteOrgProfile() {
  return apiFetch('/api/organization', { method: 'DELETE' });
}
