import { useState, useEffect } from 'react';
import { Edit2, Trash2, UserPlus, User } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Modal from '../../components/common/Modal.jsx';
import Input from '../../components/common/Input.jsx';
import Select from '../../components/common/Select.jsx';
import Textarea from '../../components/common/Textarea.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import StatusBadge from '../../components/common/StatusBadge.jsx';
import { updateContract, deleteContract } from '../../api/contracts.js';
import { getParties, addParty, updateParty, deleteParty } from '../../api/parties.js';
import { getContractStatus } from '../../api/export.js';
import {
  STATUS_OPTIONS, PARTY_ROLE_OPTIONS, PARTY_ROLE_LABELS, LEGAL_ENTITY_OPTIONS
} from '../../utils/labels.js';
import { formatDate } from '../../utils/date.js';
import { useNavigate } from 'react-router-dom';
import './OverviewTab.css';

export default function OverviewTab({ contractId, contract, onContractUpdate }) {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [parties, setParties] = useState([]);
  const [status, setStatus] = useState(null);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [addPartyOpen, setAddPartyOpen] = useState(false);
  const [editParty, setEditParty] = useState(null);

  // Edit form
  const [editForm, setEditForm] = useState({ title: contract.title, status: contract.status, description: contract.description || '', tags: contract.tags || '' });
  const [editLoading, setEditLoading] = useState(false);

  // Party form
  const [partyForm, setPartyForm] = useState({ party_role: '', party_name: '', legal_entity_type: '', address_line1: '', city: '', state: '', postal_code: '', country: 'India', contact_person: '', email: '', phone: '' });
  const [partyLoading, setPartyLoading] = useState(false);

  useEffect(() => {
    getParties(contractId).then(setParties).catch(() => setParties([]));
    getContractStatus(contractId).then(setStatus).catch(() => {});
  }, [contractId]);

  const handleEditSave = async () => {
    setEditLoading(true);
    try {
      await updateContract(contractId, editForm);
      showToast('Contract updated', 'success');
      setEditOpen(false);
      onContractUpdate();
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setEditLoading(false); }
  };

  const handleDelete = async () => {
    try {
      await deleteContract(contractId);
      showToast('Contract deleted', 'success');
      navigate('/contracts');
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleAddParty = async () => {
    setPartyLoading(true);
    try {
      if (editParty) {
        await updateParty(contractId, editParty.id, partyForm);
        showToast('Party updated', 'success');
      } else {
        await addParty(contractId, partyForm);
        showToast('Party added', 'success');
      }
      const updated = await getParties(contractId);
      setParties(updated);
      setAddPartyOpen(false);
      setEditParty(null);
      setPartyForm({ party_role: '', party_name: '', legal_entity_type: '', address_line1: '', city: '', state: '', postal_code: '', country: 'India', contact_person: '', email: '', phone: '' });
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setPartyLoading(false); }
  };

  const openEditParty = (party) => {
    setEditParty(party);
    setPartyForm({ party_role: party.party_role, party_name: party.party_name, legal_entity_type: party.legal_entity_type || '', address_line1: party.address_line1 || '', city: party.city || '', state: party.state || '', postal_code: party.postal_code || '', country: party.country || 'India', contact_person: party.contact_person || '', email: party.email || '', phone: party.phone || '' });
    setAddPartyOpen(true);
  };

  const handleDeleteParty = async (partyId) => {
    try {
      await deleteParty(contractId, partyId);
      setParties((p) => p.filter((x) => x.id !== partyId));
      showToast('Party removed', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const pf = (key) => (e) => setPartyForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="overview-tab">
      {/* Contract info */}
      <div className="overview-section">
        <div className="overview-section__header">
          <h3>Contract Information</h3>
          <div style={{ display: 'flex', gap: 'var(--sp-2)' }}>
            <Button variant="ghost" size="sm" icon={Edit2} onClick={() => setEditOpen(true)}>Edit</Button>
            {contract.status === 'draft' && (
              <Button variant="ghost" size="sm" icon={Trash2} onClick={() => setDeleteOpen(true)} style={{ color: 'var(--fn-danger)' }}>Delete</Button>
            )}
          </div>
        </div>
        <div className="overview-grid">
          <div className="overview-field">
            <span className="overview-field__label">Status</span>
            <span className="overview-field__value"><StatusBadge status={contract.status} /></span>
          </div>
          <div className="overview-field">
            <span className="overview-field__label">Created</span>
            <span className="overview-field__value">{formatDate(contract.created_at)}</span>
          </div>
          <div className="overview-field">
            <span className="overview-field__label">Updated</span>
            <span className="overview-field__value">{formatDate(contract.updated_at)}</span>
          </div>
          {contract.description && (
            <div className="overview-field overview-field--full">
              <span className="overview-field__label">Description</span>
              <span className="overview-field__value">{contract.description}</span>
            </div>
          )}
          {contract.tags && (
            <div className="overview-field overview-field--full">
              <span className="overview-field__label">Tags</span>
              <span className="overview-field__value overview-field__tags">
                {contract.tags.split(',').map((t) => (
                  <span key={t} className="tag">{t.trim()}</span>
                ))}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Generation readiness */}
      {status && (
        <div className="overview-section">
          <h3 className="overview-section__header">Generation Readiness</h3>
          <div className="readiness-row">
            <div className="readiness-item">
              <span className="readiness-item__num">{status.active_clauses_count ?? '--'}</span>
              <span className="readiness-item__label">Active Clauses</span>
            </div>
            <div className="readiness-item">
              <span className="readiness-item__num">{status.filled_parameters ?? '--'}</span>
              <span className="readiness-item__label">Filled Parameters</span>
            </div>
            <div className="readiness-item">
              <span className="readiness-item__num" style={{ color: status.is_ready ? 'var(--fn-success)' : 'var(--fn-warning)' }}>
                {status.is_ready ? 'Ready' : 'Incomplete'}
              </span>
              <span className="readiness-item__label">Status</span>
            </div>
          </div>
          {status.next_step && (
            <p style={{ fontSize: '0.8125rem', color: 'var(--ink-tertiary)', margin: 0 }}>
              Next: {status.next_step}
            </p>
          )}
        </div>
      )}

      {/* Parties */}
      <div className="overview-section">
        <div className="overview-section__header">
          <h3>Parties</h3>
          <Button variant="secondary" size="sm" icon={UserPlus} onClick={() => { setEditParty(null); setAddPartyOpen(true); }}>
            Add Party
          </Button>
        </div>

        {parties.length === 0 ? (
          <p style={{ color: 'var(--ink-tertiary)', fontSize: '0.875rem' }}>No parties added yet.</p>
        ) : (
          <div className="parties-list">
            {parties.map((party) => (
              <div key={party.id} className="party-row">
                <div className="party-row__icon">
                  <User size={16} strokeWidth={1.5} />
                </div>
                <div className="party-row__info">
                  <span className="party-row__role text-mono">{PARTY_ROLE_LABELS[party.party_role] || party.party_role}</span>
                  <span className="party-row__name">{party.party_name}</span>
                  {party.email && <span className="party-row__email">{party.email}</span>}
                  {party.legal_entity_type && <span className="party-row__type">{party.legal_entity_type}</span>}
                </div>
                <div className="party-row__actions">
                  <Button variant="ghost" size="sm" icon={Edit2} onClick={() => openEditParty(party)} />
                  <Button variant="ghost" size="sm" icon={Trash2} onClick={() => handleDeleteParty(party.id)} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Contract Modal */}
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          <Input label="Title" value={editForm.title} onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))} />
          <Select label="Status" value={editForm.status} onChange={(e) => setEditForm((f) => ({ ...f, status: e.target.value }))} options={STATUS_OPTIONS} />
          <Textarea label="Description" value={editForm.description} onChange={(e) => setEditForm((f) => ({ ...f, description: e.target.value }))} rows={3} />
          <Input label="Tags" value={editForm.tags} onChange={(e) => setEditForm((f) => ({ ...f, tags: e.target.value }))} hint="Comma-separated" />
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
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
        <p>Are you sure you want to delete <strong>{contract.title}</strong>? This action cannot be undone.</p>
      </Modal>

      {/* Add/Edit Party Modal */}
      <Modal
        isOpen={addPartyOpen}
        onClose={() => { setAddPartyOpen(false); setEditParty(null); }}
        title={editParty ? 'Edit Party' : 'Add Party'}
        footer={
          <>
            <Button variant="ghost" onClick={() => { setAddPartyOpen(false); setEditParty(null); }}>Cancel</Button>
            <Button loading={partyLoading} onClick={handleAddParty}>{editParty ? 'Save' : 'Add'}</Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          <Select label="Role" value={partyForm.party_role} onChange={pf('party_role')} options={PARTY_ROLE_OPTIONS} placeholder="Select role" required />
          <Input label="Name" value={partyForm.party_name} onChange={pf('party_name')} placeholder="Company or individual name" required />
          <Select label="Entity Type" value={partyForm.legal_entity_type} onChange={pf('legal_entity_type')} options={LEGAL_ENTITY_OPTIONS} placeholder="Select entity type" />
          <Input label="Email" type="email" value={partyForm.email} onChange={pf('email')} />
          <Input label="Phone" value={partyForm.phone} onChange={pf('phone')} />
          <Input label="Contact Person" value={partyForm.contact_person} onChange={pf('contact_person')} />
          <Input label="Address" value={partyForm.address_line1} onChange={pf('address_line1')} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-3)' }}>
            <Input label="City" value={partyForm.city} onChange={pf('city')} />
            <Input label="State" value={partyForm.state} onChange={pf('state')} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-3)' }}>
            <Input label="Postal Code" value={partyForm.postal_code} onChange={pf('postal_code')} />
            <Input label="Country" value={partyForm.country} onChange={pf('country')} />
          </div>
        </div>
      </Modal>
    </div>
  );
}
