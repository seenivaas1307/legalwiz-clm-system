import { apiFetch } from './client.js';

export async function generateContract(contractId) {
  return apiFetch(`/api/contracts/${contractId}/generate`, { method: 'POST' });
}

export async function previewContract(contractId) {
  return apiFetch(`/api/contracts/${contractId}/preview`);
}

export async function previewContractHtml(contractId) {
  return apiFetch(`/api/contracts/${contractId}/preview/html`);
}

export async function getContractStatus(contractId) {
  return apiFetch(`/api/contracts/${contractId}/status`);
}

export async function downloadPdf(contractId, watermark = null) {
  const params = watermark ? `?watermark=${encodeURIComponent(watermark)}` : '';
  const response = await apiFetch(`/api/contracts/${contractId}/export/pdf${params}`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `contract_${contractId}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function downloadDocx(contractId) {
  const response = await apiFetch(`/api/contracts/${contractId}/export/docx`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `contract_${contractId}.docx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
