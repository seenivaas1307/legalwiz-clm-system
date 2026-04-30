// api/savedParties.js
import { apiFetch } from './client.js';

/** List all saved parties for the current user. */
export async function listSavedParties() {
  return apiFetch('/api/saved-parties');
}

/** Save a new party to the directory. */
export async function createSavedParty(data) {
  return apiFetch('/api/saved-parties', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/** Update an existing saved party by ID. */
export async function updateSavedParty(id, data) {
  return apiFetch(`/api/saved-parties/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/** Delete a saved party by ID. */
export async function deleteSavedParty(id) {
  return apiFetch(`/api/saved-parties/${id}`, { method: 'DELETE' });
}
