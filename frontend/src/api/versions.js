import { apiFetch } from './client.js';

export async function listVersions(contractId) {
  return apiFetch(`/api/contracts/${contractId}/versions`);
}

export async function getVersion(contractId, versionNumber) {
  return apiFetch(`/api/contracts/${contractId}/versions/${versionNumber}`);
}

export async function createVersion(contractId, changeSummary = 'Manual snapshot') {
  return apiFetch(`/api/contracts/${contractId}/versions`, {
    method: 'POST',
    body: JSON.stringify({ change_summary: changeSummary }),
  });
}

export async function restoreVersion(contractId, versionNumber) {
  return apiFetch(`/api/contracts/${contractId}/versions/${versionNumber}/restore`, {
    method: 'POST',
  });
}

export async function compareVersions(contractId, v1, v2) {
  return apiFetch(`/api/contracts/${contractId}/versions/${v1}/compare/${v2}`);
}
