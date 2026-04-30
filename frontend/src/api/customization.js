import { apiFetch } from './client.js';

export async function customizeClause(contractId, clauseDbId, instruction) {
  return apiFetch(`/api/contracts/${contractId}/clauses/${clauseDbId}/customize`, {
    method: 'POST',
    body: JSON.stringify({ instruction }),
  });
}

export async function applyCustomization(contractId, clauseDbId, customizedText) {
  return apiFetch(`/api/contracts/${contractId}/clauses/${clauseDbId}/apply-customization`, {
    method: 'POST',
    body: JSON.stringify({ customized_text: customizedText }),
  });
}

export async function revertCustomization(contractId, clauseDbId) {
  return apiFetch(`/api/contracts/${contractId}/clauses/${clauseDbId}/revert-customization`, {
    method: 'POST',
  });
}
