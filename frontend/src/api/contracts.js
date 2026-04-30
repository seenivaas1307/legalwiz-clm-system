import { apiFetch } from './client.js';

export async function listContracts({ limit = 50, offset = 0, contractType, status } = {}) {
  const params = new URLSearchParams();
  params.set('limit', limit);
  params.set('offset', offset);
  if (contractType) params.set('contract_type', contractType);
  if (status) params.set('status', status);
  return apiFetch(`/api/contracts?${params}`);
}

export async function getContract(id) {
  return apiFetch(`/api/contracts/${id}`);
}

export async function createContract({ title, contractType, jurisdiction, description, tags }) {
  return apiFetch('/api/contracts', {
    method: 'POST',
    body: JSON.stringify({
      title,
      contract_type: contractType,
      jurisdiction,
      description: description || null,
      tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : null,
    }),
  });
}

export async function updateContract(id, updates) {
  const body = {};
  if (updates.title !== undefined) body.title = updates.title;
  if (updates.status !== undefined) body.status = updates.status;
  if (updates.description !== undefined) body.description = updates.description;
  if (updates.tags !== undefined) body.tags = updates.tags;
  return apiFetch(`/api/contracts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

export async function deleteContract(id) {
  return apiFetch(`/api/contracts/${id}`, { method: 'DELETE' });
}
