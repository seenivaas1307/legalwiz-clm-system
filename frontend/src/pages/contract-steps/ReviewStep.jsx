/**
 * ReviewStep — Step 5: Review & Export
 *
 * Two-column layout:
 *   LEFT  — live contract preview (scrollable document, placeholder highlights, refresh)
 *   RIGHT — sticky panel: pre-flight checklist, export buttons (PDF/DOCX), e-sign
 *
 * Features:
 *  - Calls /preview to assemble the contract with all substituted values
 *  - Highlighted unfilled placeholders (amber marks) so user can spot gaps at a glance
 *  - Pre-flight checklist: parties added, clauses generated, % parameters filled, completeness
 *  - Download PDF / DOCX
 *  - Send for e-signature via DocuSign modal
 *  - Check signing status
 *  - "Back" to FillDetails; finish marks the stepper done
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Eye, RefreshCw, CheckCircle, XCircle, AlertTriangle,
  FileDown, FileText, Send, Clock, ChevronLeft, ShieldCheck,
} from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Input from '../../components/common/Input.jsx';
import Textarea from '../../components/common/Textarea.jsx';
import Modal from '../../components/common/Modal.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { previewContract, getContractStatus, downloadPdf, downloadDocx } from '../../api/export.js';
import { sendForSigning, getSigningStatus, creatorSign, sendToPartyB, saveCreatorSignature } from '../../api/esign.js';
import { updateContract } from '../../api/contracts.js';
import { parsePlaceholders } from '../../utils/date.js';
import './ReviewStep.css';

// ── Rendered clause text with highlighted placeholders ───────────────────────
function ClauseText({ text }) {
  const segments = parsePlaceholders(text || '');
  return (
    <span>
      {segments.map((seg, i) =>
        seg.type === 'placeholder'
          ? <mark key={i} className="placeholder-highlight">{seg.content}</mark>
          : <span key={i}>{seg.content}</span>
      )}
    </span>
  );
}

// ── Pre-flight item ──────────────────────────────────────────────────────────
function PreflightItem({ icon: Icon, label, status, detail }) {
  const cls = `preflight-item preflight-item--${status}`;
  return (
    <div className={cls}>
      <Icon size={14} strokeWidth={2} />
      <span>
        {label}
        {detail && (
          <span style={{ marginLeft: 6, fontSize: '0.75rem', opacity: 0.75 }}>
            ({detail})
          </span>
        )}
      </span>
    </div>
  );
}

// ── Main ReviewStep ──────────────────────────────────────────────────────────
export default function ReviewStep({
  contractId, contract, onPrev, markDone,
}) {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [preview, setPreview]           = useState(null);
  const [status, setStatus]             = useState(null);
  const [previewLoading, setPreviewLoading] = useState(true);
  const [refreshing, setRefreshing]     = useState(false);

  // Export loading
  const [pdfLoading, setPdfLoading]     = useState(false);
  const [docxLoading, setDocxLoading]   = useState(false);

  // E-sign
  const [esignOpen, setEsignOpen]       = useState(false);
  const [esignForm, setEsignForm]       = useState({
    signerEmail: '', signerName: '', emailSubject: '', emailBody: '',
  });
  const [esignLoading, setEsignLoading] = useState(false);
  const [signingStatus, setSigningStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(false);

  // Creator signature
  const [creatorSignature, setCreatorSignature] = useState('');
  const [creatorSigned, setCreatorSigned] = useState(false);
  const [creatorSignedName, setCreatorSignedName] = useState('');
  const [creatorSignedAt, setCreatorSignedAt] = useState('');

  // ── Load preview + status ────────────────────────────────────────────────
  const loadPreview = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setPreviewLoading(true);
    try {
      const [p, s] = await Promise.allSettled([
        previewContract(contractId),
        getContractStatus(contractId),
      ]);
      if (p.status === 'fulfilled') setPreview(p.value);
      if (s.status === 'fulfilled') setStatus(s.value);
    } catch { /* silent */ }
    finally {
      setPreviewLoading(false);
      setRefreshing(false);
    }
  }, [contractId]);

  useEffect(() => { loadPreview(); }, [loadPreview]);

  // Load signing status on mount
  useEffect(() => { handleCheckStatus(); }, [contractId]);

  // Auto-transition to "in_review" when Review step is reached
  useEffect(() => {
    if (contract?.status === 'draft') {
      updateContract(contractId, { status: 'in_review' }).catch(() => {});
    }
  }, [contractId]);

  // ── Export ───────────────────────────────────────────────────────────────
  const handlePdf = async () => {
    setPdfLoading(true);
    try { await downloadPdf(contractId); showToast('PDF downloaded', 'success'); }
    catch (err) { showToast(err.message || 'PDF export failed', 'error'); }
    finally { setPdfLoading(false); }
  };

  const handleDocx = async () => {
    setDocxLoading(true);
    try { await downloadDocx(contractId); showToast('DOCX downloaded', 'success'); }
    catch (err) { showToast(err.message || 'DOCX export failed', 'error'); }
    finally { setDocxLoading(false); }
  };

  const [esignError, setEsignError]     = useState(null);

  // ── E-sign: Step 1 — Creator signs in-app ───────────────────────────────
  const handleCreatorSign = async () => {
    if (!creatorSignature.trim()) return;
    setEsignLoading(true);
    try {
      // Save signature to backend (updates PDF + contract status)
      const result = await saveCreatorSignature(contractId, creatorSignature.trim());
      setCreatorSigned(true);
      setCreatorSignedName(result.signature_name);
      setCreatorSignedAt(result.signature_date);
      showToast('Contract signed by creator', 'success');
      // Auto-open the modal to ask for Party B's email
      setEsignOpen(true);
      // Refresh preview to show updated signature in document
      loadPreview(true);
    } catch (err) {
      showToast(err.message || 'Signing failed', 'error');
    } finally {
      setEsignLoading(false);
    }
  };

  // ── E-sign: Step 2 — Send to Party B via DocuSign ─────────────────────
  const handleEsign = async () => {
    setEsignLoading(true);
    setEsignError(null);
    try {
      await sendForSigning(contractId, esignForm);
      showToast('Sent for signature via DocuSign', 'success');
      setEsignOpen(false);
      // Update status to signed
      try {
        await updateContract(contractId, { status: 'signed' });
      } catch { /* non-critical */ }
    } catch (err) {
      // Extract clean error message from API response
      let errMsg = 'E-sign service failed';
      try {
        const parsed = typeof err.message === 'string' && err.message.startsWith('{')
          ? JSON.parse(err.message)
          : null;
        errMsg = parsed?.message || parsed?.detail || err.message || errMsg;
      } catch {
        errMsg = err.message || errMsg;
      }
      // Show both as toast and inline in the modal
      setEsignError(errMsg);
      showToast(errMsg, 'error');
    } finally {
      setEsignLoading(false);
    }
  };

  const handleCheckStatus = async () => {
    setStatusLoading(true);
    try {
      const s = await getSigningStatus(contractId);
      setSigningStatus(s);
    } catch (err) {
      showToast(err.message || 'Status check failed', 'error');
    } finally {
      setStatusLoading(false);
    }
  };

  const ef = (key) => (e) => setEsignForm((f) => ({ ...f, [key]: e.target.value }));

  const handleFinish = async () => {
    markDone('review');
    try {
      await updateContract(contractId, { status: 'approved' });
      showToast('Contract finalized and marked as approved!', 'success');
      setTimeout(() => navigate('/contracts'), 1200);
    } catch {
      showToast('Contract review complete!', 'success');
      setTimeout(() => navigate('/contracts'), 1200);
    }
  };

  // ── Pre-flight checklist ─────────────────────────────────────────────────
  const hasClauses  = (preview?.clauses?.length ?? 0) > 0;
  const isComplete  = preview?.is_complete ?? false;
  const missingParams = preview?.missing_parameters ?? [];
  const wordCount   = preview?.word_count ?? 0;
  const filledCount = status?.filled_parameters ?? 0;
  const totalParams = status?.total_parameters ?? 0;
  const pct = totalParams > 0 ? Math.round((filledCount / totalParams) * 100) : 0;
  const hasParties  = (status?.parties_count ?? 0) > 0 || (preview?.contract?.parties?.length ?? 0) > 0;

  // ── Loading state ────────────────────────────────────────────────────────
  if (previewLoading) return <LoadingState message="Assembling contract preview…" />;

  return (
    <div className="review-step">

      {/* ── Ready / Incomplete banner ───────────────────────────────────── */}
      <div className={`review-ready-banner review-ready-banner--${isComplete ? 'ready' : 'incomplete'}`}>
        {isComplete
          ? <><CheckCircle size={18} /> Contract is complete and ready to export.</>
          : <><AlertTriangle size={18} /> {missingParams.length} parameter(s) still unfilled — highlighted below in amber.</>
        }
      </div>

      <div className="review-layout">

        {/* ── LEFT: Contract preview ─────────────────────────────────────── */}
        <div>
          {/* Refresh bar */}
          <div className="review-doc-bar">
            <span className="review-doc-bar__title">
              <Eye size={13} />
              Contract Preview
            </span>
            <Button
              variant="ghost"
              size="sm"
              icon={RefreshCw}
              loading={refreshing}
              onClick={() => loadPreview(true)}
            >
              Refresh
            </Button>
          </div>

          {/* Missing params alert */}
          {missingParams.length > 0 && (
            <div className="review-alert">
              <AlertTriangle size={15} />
              <div>
                <strong>{missingParams.length} unfilled placeholder(s):</strong>
                <div className="review-alert__params">
                  {missingParams.map((p) => (
                    <span key={p.parameter_id || p} className="review-alert__param">
                      {p.parameter_name || p}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Document body */}
          {preview ? (
            <div className="review-document">
              <div className="review-document__cover">
                <h2 className="review-document__title">
                  {preview.contract?.title || contract.title}
                </h2>
                <p className="review-document__meta">
                  {(preview.contract?.contract_type || contract.contract_type)?.replace(/_/g, ' ')}&nbsp;
                  &bull;&nbsp;
                  {preview.contract?.jurisdiction || contract.jurisdiction}
                </p>
                <hr className="review-document__divider" />
              </div>

              <div className="review-document__body">
                {(preview.clauses || []).map((clause, idx) => (
                  <div key={clause.id || idx} className="review-clause">
                    <div className="review-clause__header">
                      <span className="review-clause__num">{idx + 1}.</span>
                      <span className="review-clause__type">
                        {clause.clause_type_name || clause.clause_type}
                      </span>
                    </div>
                    <div className="review-clause__text">
                      <ClauseText text={clause.rendered_text || clause.text || clause.raw_text || clause.overridden_text || ''} />
                    </div>
                    {idx < (preview.clauses.length - 1) && <hr className="review-clause__sep" />}
                  </div>
                ))}
              </div>

              <div className="review-document__footer">
                <span className="review-document__end">— End of Contract —</span>
                {wordCount > 0 && (
                  <span className="review-document__wordcount">
                    {wordCount.toLocaleString()} words
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div style={{ padding: 'var(--sp-8)', textAlign: 'center', color: 'var(--ink-tertiary)' }}>
              Preview unavailable — generate clauses first.
            </div>
          )}
        </div>

        {/* ── RIGHT: Sticky action panel ────────────────────────────────── */}
        <div className="review-panel">

          {/* Pre-flight checklist */}
          <div className="review-panel-card">
            <div className="review-panel-card__header">
              <ShieldCheck size={13} />
              Pre-flight Checklist
            </div>
            <div className="review-panel-card__body">
              <div className="preflight-list">
                <PreflightItem
                  icon={hasParties ? CheckCircle : XCircle}
                  status={hasParties ? 'pass' : 'fail'}
                  label="Parties added"
                />
                <PreflightItem
                  icon={hasClauses ? CheckCircle : XCircle}
                  status={hasClauses ? 'pass' : 'fail'}
                  label="Clauses generated"
                  detail={hasClauses ? `${preview.clauses.length} clauses` : undefined}
                />
                <PreflightItem
                  icon={totalParams > 0 ? (pct >= 90 ? CheckCircle : pct >= 50 ? AlertTriangle : XCircle) : Clock}
                  status={totalParams === 0 ? 'skip' : pct >= 90 ? 'pass' : pct >= 50 ? 'warn' : 'fail'}
                  label="Parameters filled"
                  detail={totalParams > 0 ? `${pct}%` : 'none yet'}
                />
                <PreflightItem
                  icon={isComplete ? CheckCircle : AlertTriangle}
                  status={isComplete ? 'pass' : 'warn'}
                  label="Contract complete"
                  detail={isComplete ? undefined : `${missingParams.length} remaining`}
                />
              </div>
            </div>
          </div>

          {/* Export */}
          <div className="review-panel-card">
            <div className="review-panel-card__header">
              <FileDown size={13} />
              Export Contract
            </div>
            <div className="review-panel-card__body">
              <div className="export-btn-row">
                <Button
                  icon={FileDown}
                  loading={pdfLoading}
                  onClick={handlePdf}
                  style={{ justifyContent: 'flex-start' }}
                >
                  Download PDF
                </Button>
                <Button
                  variant="secondary"
                  icon={FileText}
                  loading={docxLoading}
                  onClick={handleDocx}
                  style={{ justifyContent: 'flex-start' }}
                >
                  Download DOCX
                </Button>
              </div>
            </div>
          </div>

          {/* E-signature — Two-step flow */}
          <div className="review-panel-card">
            <div className="review-panel-card__header">
              <Send size={13} />
              E-Signature
            </div>
            <div className="review-panel-card__body">

              {/* Step 1: Creator signs in-app */}
              {!creatorSigned && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--ink-tertiary)', margin: 0 }}>
                    Sign this contract as the creator, then send to the other party.
                  </p>
                  <div style={{
                    border: '2px dashed var(--border-medium)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--sp-4)',
                    textAlign: 'center',
                    background: 'var(--paper-inset)',
                  }}>
                    <input
                      type="text"
                      value={creatorSignature}
                      onChange={(e) => setCreatorSignature(e.target.value)}
                      placeholder="Type your full name to sign"
                      style={{
                        width: '100%',
                        border: 'none',
                        background: 'transparent',
                        fontSize: '1.25rem',
                        fontFamily: "'Georgia', 'Times New Roman', serif",
                        fontStyle: 'italic',
                        textAlign: 'center',
                        color: 'var(--ink-primary)',
                        outline: 'none',
                        padding: 'var(--sp-2)',
                      }}
                    />
                    {creatorSignature && (
                      <p style={{ fontSize: '0.6875rem', color: 'var(--ink-ghost)', margin: 'var(--sp-2) 0 0' }}>
                        By signing, you agree to the terms of this contract.
                      </p>
                    )}
                  </div>
                  <Button
                    icon={CheckCircle}
                    onClick={handleCreatorSign}
                    loading={esignLoading}
                    disabled={!creatorSignature.trim()}
                  >
                    Sign as Creator
                  </Button>
                </div>
              )}

              {/* Step 2: Creator signed — send to other party */}
              {creatorSigned && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
                  <div style={{
                    padding: 'var(--sp-3)',
                    background: 'var(--fn-success-light)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '0.8125rem',
                    color: 'var(--fn-success)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--sp-2)',
                  }}>
                    <CheckCircle size={14} />
                    Signed by {creatorSignedName} on {creatorSignedAt}
                  </div>
                  <Button
                    icon={Send}
                    onClick={() => setEsignOpen(true)}
                  >
                    Send to Other Party via DocuSign
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    loading={statusLoading}
                    onClick={handleCheckStatus}
                  >
                    Check Status
                  </Button>
                </div>
              )}

              {/* Status display — only after creator signed */}
              {creatorSigned && signingStatus && signingStatus.signing_status !== 'not_sent' && (
                <div className="esign-status" style={{ marginTop: 'var(--sp-3)' }}>
                  <div className="esign-status__row">
                    <span className="esign-status__label">Status</span>
                    <span className="esign-status__value">{signingStatus.signing_status}</span>
                  </div>
                  {signingStatus.envelope_id && (
                    <div className="esign-status__row">
                      <span className="esign-status__label">Envelope</span>
                      <span className="esign-status__value" style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>
                        {signingStatus.envelope_id}
                      </span>
                    </div>
                  )}
                  {signingStatus.signers && signingStatus.signers.map((s, i) => (
                    <div key={i} className="esign-status__row" style={{ padding: 'var(--sp-2) 0' }}>
                      <span style={{ fontSize: '0.8125rem' }}>{s.name}</span>
                      <span>{s.status === 'completed' ? '✅ Signed' : s.status === 'delivered' ? '📩 Delivered' : s.status === 'sent' ? '📤 Sent' : s.status}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Step nav ─────────────────────────────────────────────────────── */}
      <div className="step-nav">
        <Button variant="ghost" icon={ChevronLeft} onClick={onPrev}>Back</Button>
        <Button
          variant="primary"
          icon={CheckCircle}
          onClick={handleFinish}
          disabled={!isComplete}
          title={!isComplete ? 'Fill all parameters before finishing' : undefined}
        >
          Finish Contract
        </Button>
      </div>

      {/* ── E-sign modal ──────────────────────────────────────────────────── */}
      <Modal
        isOpen={esignOpen}
        onClose={() => setEsignOpen(false)}
        title="Send to Other Party"
        footer={
          <>
            <Button variant="ghost" onClick={() => setEsignOpen(false)}>Cancel</Button>
            <Button
              loading={esignLoading}
              onClick={handleEsign}
              disabled={!esignForm.signerEmail || !esignForm.signerName}
            >
              Send via DocuSign
            </Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          <p style={{ fontSize: '0.8125rem', color: 'var(--ink-tertiary)', margin: 0 }}>
            Enter the other party's details. They will receive an email from DocuSign to sign the contract.
          </p>
          {esignError && (
            <div style={{
              padding: 'var(--sp-3) var(--sp-4)',
              background: 'var(--fn-error-light, #fef2f2)',
              border: '1px solid var(--fn-error, #ef4444)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--fn-error, #ef4444)',
              fontSize: '0.8125rem',
              lineHeight: 1.5,
            }}>
              ⚠️ {esignError}
            </div>
          )}
          <Input
            label="Signer Email"
            type="email"
            value={esignForm.signerEmail}
            onChange={ef('signerEmail')}
            required
          />
          <Input
            label="Signer Name"
            value={esignForm.signerName}
            onChange={ef('signerName')}
            required
          />
          <Input
            label="Email Subject"
            value={esignForm.emailSubject}
            onChange={ef('emailSubject')}
            placeholder="Please sign this contract"
          />
          <Textarea
            label="Email Message"
            value={esignForm.emailBody}
            onChange={ef('emailBody')}
            rows={3}
            placeholder="Optional message to the signer…"
          />
        </div>
      </Modal>
    </div>
  );
}
