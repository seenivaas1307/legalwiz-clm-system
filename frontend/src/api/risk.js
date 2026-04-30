import { apiFetch } from './client.js';

export async function getQuickRisk(contractId) {
  return apiFetch(`/api/contracts/${contractId}/risk-analysis/quick`);
}

export async function getFullRiskAnalysis(contractId) {
  return apiFetch(`/api/contracts/${contractId}/risk-analysis`);
}
