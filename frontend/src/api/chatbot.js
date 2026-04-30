import { apiFetch } from './client.js';

export async function sendMessage(contractId, message, contextFilter = null) {
  return apiFetch(`/api/contracts/${contractId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message, context_filter: contextFilter }),
  });
}

export async function getChatHistory(contractId, limit = 50) {
  return apiFetch(`/api/contracts/${contractId}/chat/history?limit=${limit}`);
}

export async function clearChatHistory(contractId) {
  return apiFetch(`/api/contracts/${contractId}/chat/history`, { method: 'DELETE' });
}
