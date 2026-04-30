import { apiFetch } from './client.js';

export async function generateClauses(contractId, defaultVariant = 'Moderate') {
  return apiFetch(
    `/api/contracts/${contractId}/clauses/generate?default_variant=${defaultVariant}`,
    { method: 'POST' }
  );
}

export async function getActiveClauses(contractId) {
  return apiFetch(`/api/contracts/${contractId}/clauses/active`);
}

export async function getClauses(contractId, isActive = null) {
  const params = isActive !== null ? `?is_active=${isActive}` : '';
  return apiFetch(`/api/contracts/${contractId}/clauses${params}`);
}

export async function getClauseDetail(contractId, clauseDbId) {
  return apiFetch(`/api/contracts/${contractId}/clauses/${clauseDbId}`);
}

export async function switchVariant(contractId, clauseType, newVariant) {
  return apiFetch(`/api/contracts/${contractId}/clauses/switch-variant`, {
    method: 'PUT',
    body: JSON.stringify({ clause_type: clauseType, new_variant: newVariant }),
  });
}

export async function updateClause(contractId, clauseDbId, updates) {
  return apiFetch(`/api/contracts/${contractId}/clauses/${clauseDbId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

export async function deleteClause(contractId, clauseDbId) {
  return apiFetch(`/api/contracts/${contractId}/clauses/${clauseDbId}`, {
    method: 'DELETE',
  });
}

export async function deleteAllClauses(contractId) {
  return apiFetch(`/api/contracts/${contractId}/clauses`, { method: 'DELETE' });
}

export async function addOptionalClause(contractId, { clauseId, clauseType, variant, sequence }) {
  return apiFetch(`/api/contracts/${contractId}/clauses/add-optional`, {
    method: 'POST',
    body: JSON.stringify({
      clause_id: clauseId,
      clause_type: clauseType,
      variant,
      sequence,
    }),
  });
}
