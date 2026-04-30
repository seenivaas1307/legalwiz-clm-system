/**
 * SetupStep — Step 1: Contract Setup
 *
 * Shows contract metadata (type, jurisdiction, description, tags) with inline editing.
 * Displays a generation-readiness status strip.
 * "Next: Add Parties" advances to Step 2.
 */
import { useState, useEffect } from 'react';
import { FileText, Edit2, Trash2, CheckCircle, AlertCircle, ChevronRight } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Input from '../../components/common/Input.jsx';
import Select from '../../components/common/Select.jsx';
import Textarea from '../../components/common/Textarea.jsx';
import Modal from '../../components/common/Modal.jsx';
import StatusBadge from '../../components/common/StatusBadge.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { useNavigate } from 'react-router-dom';
import { updateContract, deleteContract } from '../../api/contracts.js';
import { getContractStatus } from '../../api/export.js';
import {
  STATUS_OPTIONS, CONTRACT_TYPE_LABELS, JURISDICTION_OPTIONS,
} from '../../utils/labels.js';
import { formatDate } from '../../utils/date.js';
import './SetupStep.css';

export default function SetupStep({ contractId, contract, onContractUpdate, onNext, markDone }) {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [status, setStatus]       = useState(null);
  const [editOpen, setEditOpen]   = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [editForm, setEditForm]   = useState({
    title:       contract.title,
    status:      contract.status,
    description: contract.description || '',
    tags:        Array.isArray(contract.tags)
                   ? contract.tags.join(', ')
                   : contract.tags || '',
  });
  const [editLoading, setEditLoading] = useState(false);

  useEffect(() => {
    getContractStatus(contractId).then(setStatus).catch(() => {});
  }, [contractId]);

  const ef = (key) => (e) => setEditForm((f) => ({ ...f, [key]: e.target.value }));

  const handleEditSave = async () => {
    setEditLoading(true);
    try {
      await updateContract(contractId, {
        title:       editForm.title.trim(),
        status:      editForm.status,
        description: editForm.description.trim() || null,
        tags:        editForm.tags.trim() || null,
      });
      showToast('Contract updated', 'success');
      setEditOpen(false);
      onContractUpdate();
    } catch (err) {
      showToast(err.message || 'Update failed', 'error');
    } finally {
      setEditLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteContract(contractId);
      showToast('Contract deleted', 'success');
      navigate('/contracts');
    } catch (err) {
      showToast(err.message || 'Delete failed', 'error');
    }
  };

  const handleNext = () => {
    markDone('setup');
    onNext();
  };

  // Coerce tags to an array for display
  const tagsArr = Array.isArray(contract.tags)
    ? contract.tags
    : (contract.tags || '').split(',').map((t) => t.trim()).filter(Boolean);

  return (
    <div className="setup-step">

      {/* ── Contract info card ────────────────────────────────────────── */}
      <div className="setup-card">
        <div className="setup-card__header">
          <span className="setup-card__title">
            <FileText size={15} strokeWidth={1.75} />
            Contract Information
          </span>
          <div style={{ display: 'flex', gap: 'var(--sp-2)' }}>
            <Button variant="ghost" size="sm" icon={Edit2} onClick={() => setEditOpen(true)}>
              Edit
            </Button>
            {contract.status === 'draft' && (
              <Button
                variant="ghost"
                size="sm"
                icon={Trash2}
                onClick={() => setDeleteOpen(true)}
                style={{ color: 'var(--fn-danger)' }}
              >
                Delete
              </Button>
            )}
          </div>
        </div>

        <div className="setup-info-grid">
          <div className="setup-field">
            <span className="setup-field__label">Status</span>
            <span className="setup-field__value"><StatusBadge status={contract.status} /></span>
          </div>
          <div className="setup-field">
            <span className="setup-field__label">Contract Type</span>
            <span className="setup-field__value">
              {CONTRACT_TYPE_LABELS[contract.contract_type] || contract.contract_type}
            </span>
          </div>
          <div className="setup-field">
            <span className="setup-field__label">Jurisdiction</span>
            <span className="setup-field__value">{contract.jurisdiction}</span>
          </div>
          <div className="setup-field">
            <span className="setup-field__label">Created</span>
            <span className="setup-field__value">{formatDate(contract.created_at)}</span>
          </div>
          {contract.description && (
            <div className="setup-field" style={{ gridColumn: '1 / -1' }}>
              <span className="setup-field__label">Description</span>
              <span className="setup-field__value">{contract.description}</span>
            </div>
          )}
          {tagsArr.length > 0 && (
            <div className="setup-field" style={{ gridColumn: '1 / -1' }}>
              <span className="setup-field__label">Tags</span>
              <div className="setup-tags">
                {tagsArr.map((t) => <span key={t} className="setup-tag">{t}</span>)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Readiness strip ───────────────────────────────────────────── */}
      {status && (
        <div className="setup-card">
          <div className="setup-card__header">
            <span className="setup-card__title">
              {status.is_ready
                ? <CheckCircle size={15} strokeWidth={1.75} style={{ color: 'var(--fn-success)' }} />
                : <AlertCircle size={15} strokeWidth={1.75} style={{ color: 'var(--fn-warning)' }} />
              }
              Generation Readiness
            </span>
          </div>
          <div className="setup-readiness">
            <div className="setup-readiness__item">
              <span className="setup-readiness__num">{status.active_clauses_count ?? '—'}</span>
              <span className="setup-readiness__label">Active Clauses</span>
            </div>
            <div className="setup-readiness__item">
              <span className="setup-readiness__num">{status.filled_parameters ?? '—'}</span>
              <span className="setup-readiness__label">Filled Params</span>
            </div>
            <div className="setup-readiness__item">
              <span
                className={`setup-readiness__num ${
                  status.is_ready
                    ? 'setup-readiness__status--ready'
                    : 'setup-readiness__status--pending'
                }`}
              >
                {status.is_ready ? 'Ready' : 'Incomplete'}
              </span>
              <span className="setup-readiness__label">Status</span>
            </div>
          </div>
          {status.next_step && (
            <p className="setup-hint" style={{ marginTop: 'var(--sp-3)' }}>
              Next recommended action: {status.next_step}
            </p>
          )}
        </div>
      )}

      {/* ── Step nav ──────────────────────────────────────────────────── */}
      <div className="step-nav">
        <span />
        <Button variant="primary" icon={ChevronRight} onClick={handleNext}>
          Next: Add Parties
        </Button>
      </div>

      {/* ── Edit Contract Modal ───────────────────────────────────────── */}
      <Modal
        isOpen={editOpen}
        onClose={() => setEditOpen(false)}
        title="Edit Contract"
        footer={
          <>
            <Button variant="ghost" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button loading={editLoading} onClick={handleEditSave}>Save</Button>
          </>
        }
      >
        <div className="setup-edit-form">
          <Input
            label="Title"
            value={editForm.title}
            onChange={ef('title')}
            required
          />
          <div className="form-row">
            <Select
              label="Status"
              value={editForm.status}
              onChange={ef('status')}
              options={STATUS_OPTIONS}
            />
          </div>
          <Textarea
            label="Description"
            value={editForm.description}
            onChange={ef('description')}
            rows={3}
          />
          <Input
            label="Tags"
            value={editForm.tags}
            onChange={ef('tags')}
            hint="Comma-separated"
          />
        </div>
      </Modal>

      {/* ── Delete Confirmation Modal ─────────────────────────────────── */}
      <Modal
        isOpen={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        title="Delete Contract"
        footer={
          <>
            <Button variant="ghost" onClick={() => setDeleteOpen(false)}>Cancel</Button>
            <Button variant="danger" onClick={handleDelete}>Delete</Button>
          </>
        }
      >
        <p>
          Are you sure you want to delete <strong>{contract.title}</strong>?
          This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
}
