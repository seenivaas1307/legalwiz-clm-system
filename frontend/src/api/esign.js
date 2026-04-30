import { apiFetch } from './client.js';

export async function sendForSigning(contractId, { signerEmail, signerName, emailSubject, emailBody }) {
  return apiFetch(`/api/contracts/${contractId}/esign/send`, {
    method: 'POST',
    body: JSON.stringify({
      signer_email: signerEmail,
      signer_name: signerName,
      email_subject: emailSubject || null,
      email_body: emailBody || null,
    }),
  });
}

export async function creatorSign(contractId, { partyBEmail, partyBName } = {}) {
  return apiFetch(`/api/contracts/${contractId}/esign/creator-sign`, {
    method: 'POST',
    body: JSON.stringify({
      party_b_email: partyBEmail || null,
      party_b_name: partyBName || null,
    }),
  });
}

export async function saveCreatorSignature(contractId, signatureName) {
  return apiFetch(`/api/contracts/${contractId}/esign/creator-signature`, {
    method: 'POST',
    body: JSON.stringify({ signature_name: signatureName }),
  });
}

export async function sendToPartyB(contractId, { signerEmail, signerName }) {
  return apiFetch(`/api/contracts/${contractId}/esign/send-to-party-b`, {
    method: 'POST',
    body: JSON.stringify({
      signer_email: signerEmail,
      signer_name: signerName,
    }),
  });
}

export async function getSigningUrl(contractId) {
  return apiFetch(`/api/contracts/${contractId}/esign/signing-url`);
}

export async function getSigningStatus(contractId) {
  return apiFetch(`/api/contracts/${contractId}/esign/status`);
}
