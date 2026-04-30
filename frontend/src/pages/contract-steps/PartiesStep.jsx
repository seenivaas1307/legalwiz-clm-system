/**
 * PartiesStep — Step 2: Add / manage parties + auto-fill trigger
 *
 * Features:
 *  - Saved party chips: pick from directory → instant pre-fill of the Add form
 *  - "Import from my org" button: auto-fills Party A from org profile
 *  - Party cards with Edit / Delete per card
 *  - "Run Auto-Fill" after parties are added → calls POST /parameters/auto-fill
 *    and shows how many params were populated
 *  - Advances to ClausesStep when user clicks "Next"
 */
import { useState, useEffect, useCallback } from 'react';
import {
  Users, UserPlus, Plus, Edit2, Trash2,
  Building2, Zap, CheckCircle, ChevronLeft, ChevronRight, BookUser,
  Mail, Phone, MapPin, Sparkles,
} from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Modal from '../../components/common/Modal.jsx';
import Input from '../../components/common/Input.jsx';
import Select from '../../components/common/Select.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { getParties, addParty, updateParty, deleteParty } from '../../api/parties.js';
import { getOrgProfile } from '../../api/organization.js';
import { listSavedParties } from '../../api/savedParties.js';
import { autoFillFromParties } from '../../api/autofill.js';
import { extractPartiesFromDescription } from '../../api/autofill.js';
import { PARTY_ROLE_OPTIONS, PARTY_ROLE_LABELS, LEGAL_ENTITY_OPTIONS } from '../../utils/labels.js';
import './PartiesStep.css';

const BLANK_FORM = {
  party_role: '', party_name: '', legal_entity_type: '',
  address_line1: '', city: '', state: '', postal_code: '', country: 'India',
  contact_person: '', email: '', phone: '',
};

export default function PartiesStep({
  contractId, contract, onContractUpdate, onNext, onPrev, markDone,
}) {
  const { showToast } = useToast();

  const [parties, setParties]               = useState([]);
  const [savedParties, setSavedParties]     = useState([]);
  const [orgProfile, setOrgProfile]         = useState(null);
  const [loading, setLoading]               = useState(true);
  const [autoFillResult, setAutoFillResult] = useState(null); // { filled } count
  const [autoFilling, setAutoFilling]       = useState(false);
  const [extracting, setExtracting]         = useState(false);

  // Modal state
  const [modalOpen, setModalOpen]     = useState(false);
  const [editingParty, setEditingParty] = useState(null); // null = add mode
  const [form, setForm]               = useState(BLANK_FORM);
  const [formLoading, setFormLoading] = useState(false);

  // Load everything in parallel
  const loadData = useCallback(async () => {
    setLoading(true);
    const [p, sp, org] = await Promise.allSettled([
      getParties(contractId),
      listSavedParties(),
      getOrgProfile(),
    ]);
    if (p.status === 'fulfilled')  setParties(p.value ?? []);
    if (sp.status === 'fulfilled') setSavedParties(sp.value?.parties ?? sp.value ?? []);
    if (org.status === 'fulfilled') setOrgProfile(org.value);
    setLoading(false);
  }, [contractId]);

  useEffect(() => { loadData(); }, [loadData]);

  // ── Form helpers ────────────────────────────────────────────────────────
  const ff = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const openAdd = () => {
    setEditingParty(null);
    setForm(BLANK_FORM);
    setModalOpen(true);
  };

  const openEdit = (party) => {
    setEditingParty(party);
    setForm({
      party_role:        party.party_role,
      party_name:        party.party_name,
      legal_entity_type: party.legal_entity_type || '',
      address_line1:     party.address_line1 || '',
      city:              party.city || '',
      state:             party.state || '',
      postal_code:       party.postal_code || '',
      country:           party.country || 'India',
      contact_person:    party.contact_person || '',
      email:             party.email || '',
      phone:             party.phone || '',
    });
    setModalOpen(true);
  };

  // Pre-fill form from a saved party chip click
  const prefillFromSaved = (sp) => {
    setEditingParty(null);
    setForm({
      party_role:        '',           // let user choose the role
      party_name:        sp.name || '',
      legal_entity_type: sp.legal_entity_type || '',
      address_line1:     sp.address_line1 || '',
      city:              sp.city || '',
      state:             sp.state || '',
      postal_code:       sp.postal_code || '',
      country:           sp.country || 'India',
      contact_person:    sp.contact_person || '',
      email:             sp.email || '',
      phone:             sp.phone || '',
    });
    setModalOpen(true);
  };

  // Import org profile as Party A
  const importOrgAsPartyA = () => {
    if (!orgProfile) return;
    setEditingParty(null);
    setForm({
      party_role:        'party_a',
      party_name:        orgProfile.company_name || '',
      legal_entity_type: orgProfile.legal_entity_type || '',
      address_line1:     orgProfile.address_line1 || '',
      city:              orgProfile.city || '',
      state:             orgProfile.state || '',
      postal_code:       orgProfile.postal_code || '',
      country:           orgProfile.country || 'India',
      contact_person:    orgProfile.signatory_name || '',
      email:             orgProfile.email || '',
      phone:             orgProfile.phone || '',
    });
    setModalOpen(true);
  };

  // Save (add or update)
  const handleSave = async () => {
    if (!form.party_role || !form.party_name.trim()) {
      showToast('Role and name are required', 'error');
      return;
    }
    setFormLoading(true);
    try {
      if (editingParty) {
        await updateParty(contractId, editingParty.id, form);
        showToast('Party updated', 'success');
      } else {
        await addParty(contractId, form);
        showToast('Party added', 'success');
      }
      setModalOpen(false);
      setEditingParty(null);
      const updated = await getParties(contractId);
      setParties(updated);
    } catch (err) {
      showToast(err.message || 'Failed to save party', 'error');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (partyId) => {
    try {
      await deleteParty(contractId, partyId);
      setParties((p) => p.filter((x) => x.id !== partyId));
      showToast('Party removed', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to remove party', 'error');
    }
  };

  // Auto-fill from parties
  const handleAutoFill = async () => {
    if (parties.length === 0) {
      showToast('Add at least one party first', 'error');
      return;
    }
    setAutoFilling(true);
    try {
      const result = await autoFillFromParties(contractId);
      setAutoFillResult(result);
      const count = result.auto_filled ?? result.filled ?? 0;
      if (count === 0 && result.message) {
        showToast(result.message, 'info');
      } else {
        showToast(`Auto-filled ${count} parameters from party data`, 'success');
      }
    } catch (err) {
      showToast(err.message || 'Auto-fill failed', 'error');
    } finally {
      setAutoFilling(false);
    }
  };

  // Extract parties from contract description using LLM
  const handleExtractFromDescription = async () => {
    if (!contract?.description?.trim()) {
      showToast('No description found. Add a description in the Setup step first.', 'error');
      return;
    }
    setExtracting(true);
    try {
      const result = await extractPartiesFromDescription(contractId);
      if (result.extracted > 0) {
        showToast(`Extracted ${result.extracted} party/parties from description`, 'success');
        const updated = await getParties(contractId);
        setParties(updated);
      } else {
        showToast(result.message || 'Could not extract parties from description', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Extraction failed', 'error');
    } finally {
      setExtracting(false);
    }
  };

  const handleNext = () => {
    markDone('parties');
    onNext();
  };

  if (loading) {
    return (
      <div className="parties-step">
        <div className="parties-empty">
          <p>Loading parties…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="parties-step">

      {/* ── Top action bar ──────────────────────────────────────────────── */}
      <div className="parties-step__bar">
        <span className="parties-step__heading">
          <Users size={15} strokeWidth={1.75} />
          Contract Parties
          <span style={{ fontWeight: 400, color: 'var(--ink-tertiary)', fontSize: '0.8125rem' }}>
            ({parties.length} added)
          </span>
        </span>
        <div style={{ display: 'flex', gap: 'var(--sp-2)', flexWrap: 'wrap' }}>
          {contract?.description?.trim() && (
            <Button
              variant="ghost"
              size="sm"
              icon={Sparkles}
              onClick={handleExtractFromDescription}
              loading={extracting}
              title="Use AI to extract party details from the contract description"
            >
              Extract from Description
            </Button>
          )}
          {orgProfile && (
            <Button variant="ghost" size="sm" icon={Building2} onClick={importOrgAsPartyA}>
              Import My Org
            </Button>
          )}
          <Button variant="secondary" size="sm" icon={UserPlus} onClick={openAdd}>
            Add Party
          </Button>
        </div>
      </div>

      {/* ── Saved party chip strip ──────────────────────────────────────── */}
      {savedParties.length > 0 && (
        <div className="saved-party-strip">
          <span className="saved-party-strip__label"><BookUser size={12} style={{ display: 'inline', marginRight: 4 }} />Saved</span>
          <div className="saved-party-chips">
            {savedParties.slice(0, 8).map((sp) => (
              <button
                key={sp.id}
                type="button"
                className="saved-party-chip"
                onClick={() => prefillFromSaved(sp)}
                title={`Pre-fill form with ${sp.name}`}
              >
                <Plus size={11} strokeWidth={2.5} />
                {sp.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Party cards ─────────────────────────────────────────────────── */}
      {parties.length === 0 ? (
        <div className="parties-empty">
          <Users size={32} strokeWidth={1} />
          <p>No parties added yet. Add at least two parties (Party A and Party B) to continue.</p>
          <Button variant="secondary" size="sm" icon={UserPlus} onClick={openAdd}>
            Add First Party
          </Button>
        </div>
      ) : (
        <div className="parties-grid">
          {parties.map((party) => (
            <div key={party.id} className="party-card">
              <div className="party-card__header">
                <span className="party-card__role-badge">
                  <Users size={11} strokeWidth={2} />
                  {PARTY_ROLE_LABELS[party.party_role] || party.party_role}
                </span>
                <div className="party-card__actions">
                  <Button variant="ghost" size="sm" icon={Edit2} onClick={() => openEdit(party)} />
                  <Button variant="ghost" size="sm" icon={Trash2} onClick={() => handleDelete(party.id)} />
                </div>
              </div>
              <div className="party-card__name">{party.party_name}</div>
              <div className="party-card__meta">
                {party.legal_entity_type && (
                  <span className="party-card__meta-item">
                    <Building2 size={12} strokeWidth={1.75} />
                    {party.legal_entity_type}
                  </span>
                )}
                {party.email && (
                  <span className="party-card__meta-item">
                    <Mail size={12} strokeWidth={1.75} />
                    {party.email}
                  </span>
                )}
                {party.phone && (
                  <span className="party-card__meta-item">
                    <Phone size={12} strokeWidth={1.75} />
                    {party.phone}
                  </span>
                )}
                {party.city && (
                  <span className="party-card__meta-item">
                    <MapPin size={12} strokeWidth={1.75} />
                    {[party.city, party.state, party.country].filter(Boolean).join(', ')}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Step nav ────────────────────────────────────────────────────── */}
      <div className="step-nav">
        <Button variant="ghost" icon={ChevronLeft} onClick={onPrev}>Back</Button>
        <Button
          variant="primary"
          icon={ChevronRight}
          onClick={handleNext}
          disabled={parties.length === 0}
          title={parties.length === 0 ? 'Add at least one party to continue' : undefined}
        >
          Next: Select Clauses
        </Button>
      </div>

      {/* ── Add / Edit Party Modal ───────────────────────────────────────── */}
      <Modal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditingParty(null); }}
        title={editingParty ? 'Edit Party' : 'Add Party'}
        footer={
          <>
            <Button variant="ghost" onClick={() => { setModalOpen(false); setEditingParty(null); }}>
              Cancel
            </Button>
            <Button loading={formLoading} onClick={handleSave}>
              {editingParty ? 'Save Changes' : 'Add Party'}
            </Button>
          </>
        }
      >
        <div className="party-form">
          <Select
            label="Role"
            value={form.party_role}
            onChange={ff('party_role')}
            options={PARTY_ROLE_OPTIONS}
            placeholder="Select role"
            required
          />
          <Input
            label="Name"
            value={form.party_name}
            onChange={ff('party_name')}
            placeholder="Company or individual name"
            required
          />
          <Select
            label="Entity Type"
            value={form.legal_entity_type}
            onChange={ff('legal_entity_type')}
            options={LEGAL_ENTITY_OPTIONS}
            placeholder="Select entity type"
          />
          <div className="form-row-2">
            <Input label="Email" type="email" value={form.email} onChange={ff('email')} />
            <Input label="Phone" value={form.phone} onChange={ff('phone')} />
          </div>
          <Input
            label="Contact Person"
            value={form.contact_person}
            onChange={ff('contact_person')}
          />
          <Input label="Address" value={form.address_line1} onChange={ff('address_line1')} />
          <div className="form-row-2">
            <Input label="City" value={form.city} onChange={ff('city')} />
            <Input label="State" value={form.state} onChange={ff('state')} />
          </div>
          <div className="form-row-2">
            <Input label="Postal Code" value={form.postal_code} onChange={ff('postal_code')} />
            <Input label="Country" value={form.country} onChange={ff('country')} />
          </div>
        </div>
      </Modal>
    </div>
  );
}
