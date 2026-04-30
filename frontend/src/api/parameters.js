import { apiFetch } from './client.js';

export async function getRequiredParameters(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/required`);
}

export async function getParameterValues(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/values`);
}

export async function getParameterForm(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/form`);
}

export async function getParametersGrouped(contractId, format = 'display', groupBy = 'clause') {
  const params = new URLSearchParams({ format, group_by: groupBy });
  return apiFetch(`/api/contracts/${contractId}/parameters/grouped?${params}`);
}


export async function setParameter(contractId, parameterId, value) {
  return apiFetch(`/api/contracts/${contractId}/parameters`, {
    method: 'POST',
    body: JSON.stringify({ parameter_id: parameterId, value }),
  });
}

export async function setParametersBulk(contractId, parameters) {
  return apiFetch(`/api/contracts/${contractId}/parameters/bulk`, {
    method: 'POST',
    body: JSON.stringify({ parameters }),
  });
}

export async function deleteParameter(contractId, parameterId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/${parameterId}`, {
    method: 'DELETE',
  });
}

export async function validateParameters(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/validation`);
}
