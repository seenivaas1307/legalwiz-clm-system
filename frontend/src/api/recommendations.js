import { apiFetch } from './client.js';

export async function getRecommendations(contractId) {
  return apiFetch(`/api/contracts/${contractId}/recommendations`);
}

export async function applyRecommendation(contractId, { recommendationType, clauseType, clauseId }) {
  return apiFetch(`/api/contracts/${contractId}/recommendations/apply`, {
    method: 'POST',
    body: JSON.stringify({
      recommendation_type: recommendationType,
      clause_type: clauseType,
      clause_id: clauseId,
    }),
  });
}
