import { apiFetch } from './client.js';

export async function listTemplates({ contractType, jurisdiction } = {}) {
  const params = new URLSearchParams();
  if (contractType) params.set('contract_type', contractType);
  if (jurisdiction) params.set('jurisdiction', jurisdiction);
  const qs = params.toString();
  return apiFetch(`/api/templates${qs ? '?' + qs : ''}`);
}

export async function getTemplate(templateId) {
  return apiFetch(`/api/templates/${templateId}`);
}

export async function createTemplate({ contractId, name, description, isPublic }) {
  return apiFetch('/api/templates', {
    method: 'POST',
    body: JSON.stringify({
      contract_id: contractId,
      name,
      description: description || null,
      is_public: isPublic !== undefined ? isPublic : true,
    }),
  });
}

export async function deleteTemplate(templateId) {
  return apiFetch(`/api/templates/${templateId}`, { method: 'DELETE' });
}

export async function applyTemplate(contractId, templateId) {
  return apiFetch(`/api/contracts/${contractId}/apply-template/${templateId}`, {
    method: 'POST',
  });
}
