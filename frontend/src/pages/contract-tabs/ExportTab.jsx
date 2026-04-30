import { useState } from 'react';
import { FileDown, FileText, Send } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Input from '../../components/common/Input.jsx';
import Textarea from '../../components/common/Textarea.jsx';
import Modal from '../../components/common/Modal.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { downloadPdf, downloadDocx } from '../../api/export.js';
import { sendForSigning, getSigningStatus } from '../../api/esign.js';
import './ExportTab.css';

export default function ExportTab({ contractId, contract }) {
  const { showToast } = useToast();
  const [pdfLoading, setPdfLoading] = useState(false);
  const [docxLoading, setDocxLoading] = useState(false);
  const [esignOpen, setEsignOpen] = useState(false);
  const [esignForm, setEsignForm] = useState({ signerEmail: '', signerName: '', emailSubject: '', emailBody: '' });
  const [esignLoading, setEsignLoading] = useState(false);
  const [signingStatus, setSigningStatus] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(false);

  const handlePdf = async () => {
    setPdfLoading(true);
    try {
      await downloadPdf(contractId);
      showToast('PDF downloaded', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setPdfLoading(false); }
  };

  const handleDocx = async () => {
    setDocxLoading(true);
    try {
      await downloadDocx(contractId);
      showToast('DOCX downloaded', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setDocxLoading(false); }
  };

  const handleEsign = async () => {
    setEsignLoading(true);
    try {
      await sendForSigning(contractId, esignForm);
      showToast('Sent for signature via DocuSign', 'success');
      setEsignOpen(false);
    } catch (err) {
      const detail = err.detail;
      const msg = typeof detail === 'object' && detail?.message ? detail.message : (typeof detail === 'string' ? detail : err.message);
      showToast(msg || 'Failed to send for signature', 'error');
      setEsignOpen(false);
    } finally { setEsignLoading(false); }
  };

  const checkStatus = async () => {
    setLoadingStatus(true);
    try {
      const s = await getSigningStatus(contractId);
      setSigningStatus(s);
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setLoadingStatus(false); }
  };

  const ef = (key) => (e) => setEsignForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="export-tab">
      <div className="export-section">
        <h3>Download Contract</h3>
        <p>Export the finalized contract with all parameters filled. The contract must be fully parameterized before export.</p>
        <div className="export-options">
          <div className="export-card">
            <div className="export-card__icon">
              <FileDown size={24} strokeWidth={1.5} />
            </div>
            <div className="export-card__info">
              <span className="export-card__format">PDF</span>
              <span className="export-card__desc">Print-ready document with formatting preserved.</span>
            </div>
            <Button loading={pdfLoading} onClick={handlePdf} size="sm">Download PDF</Button>
          </div>
          <div className="export-card">
            <div className="export-card__icon">
              <FileText size={24} strokeWidth={1.5} />
            </div>
            <div className="export-card__info">
              <span className="export-card__format">DOCX</span>
              <span className="export-card__desc">Editable Word document for further review.</span>
            </div>
            <Button variant="secondary" loading={docxLoading} onClick={handleDocx} size="sm">Download DOCX</Button>
          </div>
        </div>
      </div>

      <div className="export-section">
        <h3>E-Signature</h3>
        <p>Send this contract for electronic signature via DocuSign. Parties will receive an email with a link to sign.</p>
        <div style={{ display: 'flex', gap: 'var(--sp-3)' }}>
          <Button icon={Send} onClick={() => setEsignOpen(true)}>
            Send for Signature
          </Button>
          <Button variant="secondary" loading={loadingStatus} onClick={checkStatus}>
            Check Status
          </Button>
        </div>

        {signingStatus && (
          <div className="signing-status">
            <h4>Signing Status</h4>
            <div className="signing-status__grid">
              <div className="signing-field">
                <span className="signing-field__label">Status</span>
                <span className="signing-field__value">{signingStatus.signing_status || signingStatus.status}</span>
              </div>
              <div className="signing-field">
                <span className="signing-field__label">Envelope ID</span>
                <span className="signing-field__value text-mono" style={{ fontSize: '0.75rem' }}>
                  {signingStatus.envelope_id}
                </span>
              </div>
              {signingStatus.sent_at && (
                <div className="signing-field">
                  <span className="signing-field__label">Sent</span>
                  <span className="signing-field__value">{new Date(signingStatus.sent_at).toLocaleString()}</span>
                </div>
              )}
              {signingStatus.signers && signingStatus.signers.map((s, i) => (
                <div key={i} className="signing-field">
                  <span className="signing-field__label">{s.name} ({s.email})</span>
                  <span className="signing-field__value">
                    {s.status === 'completed' ? '✅ Signed' : s.status === 'delivered' ? '📩 Delivered' : s.status === 'sent' ? '📤 Sent' : s.status === 'declined' ? '❌ Declined' : s.status}
                    {s.signed_at && ` — ${new Date(s.signed_at).toLocaleString()}`}
                  </span>
                </div>
              ))}
              {!signingStatus.signers && signingStatus.signer_email && (
                <div className="signing-field">
                  <span className="signing-field__label">Signer</span>
                  <span className="signing-field__value">{signingStatus.signer_name} ({signingStatus.signer_email})</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* E-sign modal */}
      <Modal
        isOpen={esignOpen}
        onClose={() => setEsignOpen(false)}
        title="Send for Signature"
        footer={
          <>
            <Button variant="ghost" onClick={() => setEsignOpen(false)}>Cancel</Button>
            <Button loading={esignLoading} onClick={handleEsign} disabled={!esignForm.signerEmail || !esignForm.signerName}>
              Send
            </Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          <Input label="Signer Email" type="email" value={esignForm.signerEmail} onChange={ef('signerEmail')} required />
          <Input label="Signer Name" value={esignForm.signerName} onChange={ef('signerName')} required />
          <Input label="Email Subject" value={esignForm.emailSubject} onChange={ef('emailSubject')} placeholder="Please sign this contract" />
          <Textarea label="Email Message" value={esignForm.emailBody} onChange={ef('emailBody')} rows={3} placeholder="Optional message to the signer..." />
        </div>
      </Modal>
    </div>
  );
}
