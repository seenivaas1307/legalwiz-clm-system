import { apiFetch } from './client.js';

export async function getParties(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parties`);
}

export async function addParty(contractId, partyData) {
  return apiFetch(`/api/contracts/${contractId}/parties`, {
    method: 'POST',
    body: JSON.stringify(partyData),
  });
}

export async function updateParty(contractId, partyId, updates) {
  return apiFetch(`/api/contracts/${contractId}/parties/${partyId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

export async function deleteParty(contractId, partyId) {
  return apiFetch(`/api/contracts/${contractId}/parties/${partyId}`, {
    method: 'DELETE',
  });
}
