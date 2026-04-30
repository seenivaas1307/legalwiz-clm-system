// api/autofill.js
import { apiFetch } from './client.js';

/**
 * Layer 1 — Auto-fill parameters from party data.
 * Maps party fields (name, address, email…) to matching {{PLACEHOLDER}} params.
 */
export async function autoFillFromParties(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/auto-fill`, {
    method: 'POST',
  });
}

/**
 * Layer 3 — Apply smart defaults based on contract type + jurisdiction.
 * e.g. India → GOVERNING_LAW = "Laws of India"
 */
export async function applySmartDefaults(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/apply-defaults`, {
    method: 'POST',
  });
}

/**
 * Layer 4 — Cascade inference: derive related parameters from a changed one.
 * e.g. EFFECTIVE_DATE change → derive TERM_END_DATE.
 *
 * @param {string} contractId
 * @param {string} changedParameter - bare placeholder name, e.g. "EFFECTIVE_DATE"
 * @param {string} value            - the new value as a string
 */
export async function cascadeParameter(contractId, changedParameter, value) {
  return apiFetch(`/api/contracts/${contractId}/parameters/cascade`, {
    method: 'POST',
    body: JSON.stringify({ changed_parameter: changedParameter, value: String(value) }),
  });
}

/**
 * Get parameters grouped by semantic category (People/Dates/Financial/…).
 * Includes current_value + provided_by for each parameter.
 */
export async function getParametersGroupedSemantic(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parameters/grouped?group_by=semantic`);
}

/**
 * Extract parties from contract description using LLM.
 * Creates parties automatically if extraction succeeds.
 */
export async function extractPartiesFromDescription(contractId) {
  return apiFetch(`/api/contracts/${contractId}/parties/extract-from-description`, {
    method: 'POST',
  });
}
