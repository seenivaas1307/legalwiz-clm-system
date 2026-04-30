/**
 * ClausesStep — Step 3: Generate & Configure Clauses
 *
 * Improvements over ClausesTab:
 *  - Generate-first hero (empty state with prominent CTA)
 *  - Risk-coloured left border per clause card (low/medium/high/critical)
 *  - Risk legend strip
 *  - Inline expand with full text + Customize button inside the expanded body
 *  - Variant switcher rendered inline in the card header
 *  - AI Customize modal (generate preview → apply / revert)
 *  - Regenerate confirmation with clear warning
 *  - "Next: Fill Details" advances to Step 4
 */
import { useState, useEffect, useCallback } from 'react';
import {
  ListOrdered, ChevronDown, ChevronUp, RefreshCw,
  Pencil, Sparkles, ChevronLeft, ChevronRight, RotateCcw,
} from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Select from '../../components/common/Select.jsx';
import Modal from '../../components/common/Modal.jsx';
import Textarea from '../../components/common/Textarea.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import {
  getActiveClauses, generateClauses, switchVariant, deleteAllClauses,
} from '../../api/clauses.js';
import { customizeClause, applyCustomization, revertCustomization } from '../../api/customization.js';
import { VARIANT_OPTIONS } from '../../utils/labels.js';
import './ClausesStep.css';

// ── Risk helpers ────────────────────────────────────────────────────────────
function riskLevel(score) {
  if (score == null) return null;
  const s = score * 10; // stored 0–1, display 0–10
  if (s <= 3)  return 'low';
  if (s <= 5)  return 'medium';
  if (s <= 7)  return 'high';
  return 'critical';
}

// ── ClauseCard sub-component ────────────────────────────────────────────────
function ClauseCard({ clause, contractId, onRefresh, onCustomize }) {
  const [expanded, setExpanded] = useState(false);
  const [switching, setSwitching] = useState(false);
  const { showToast } = useToast();

  const handleVariantChange = async (e) => {
    const v = e.target.value;
    if (v === clause.variant) return;
    setSwitching(true);
    try {
      await switchVariant(contractId, clause.clause_type, v);
      showToast(`Switched to ${v} variant`, 'success');
      onRefresh();
    } catch (err) {
      showToast(err.message || 'Variant switch failed', 'error');
    } finally {
      setSwitching(false);
    }
  };

  const text = clause.is_customized && clause.overridden_text
    ? clause.overridden_text
    : clause.raw_text;

  const availableVariants = (clause.available_variants || [])
    .filter((v) => v.variant != null)
    .map((v) => ({ value: v.variant, label: v.variant }));

  const risk = riskLevel(clause.risk_level);

  return (
    <div className="clause-card" data-risk={risk ?? undefined}>
      {/* ── Header row (always visible) ── */}
      <div
        className="clause-card__header"
        onClick={() => setExpanded((v) => !v)}
        role="button"
        aria-expanded={expanded}
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded((v) => !v)}
      >
        <div className="clause-card__meta">
          <span className="clause-card__name">
            {clause.clause_type_name || clause.clause_type}
          </span>
          <div className="clause-card__badges">
            {clause.is_mandatory && (
              <span className="clause-badge clause-badge--required">Required</span>
            )}
            {clause.is_customized && (
              <span className="clause-badge clause-badge--customized">Customized</span>
            )}
          </div>
        </div>

        <div className="clause-card__controls" onClick={(e) => e.stopPropagation()}>
          {availableVariants.length > 1 && (
            <select
              className="clause-variant-select"
              value={clause.variant}
              onChange={handleVariantChange}
              disabled={switching}
              title="Switch clause variant"
            >
              {availableVariants.map((v) => (
                <option key={v.value} value={v.value}>{v.label}</option>
              ))}
            </select>
          )}
        </div>

        <button className="clause-expand-btn" type="button" aria-label={expanded ? 'Collapse' : 'Expand'}>
          {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
      </div>

      {/* ── Expanded body ── */}
      {expanded && (
        <div className="clause-card__body">
          <div className="clause-card__body-inner">
            <pre className="clause-card__text">{text || 'No text available.'}</pre>
            <div className="clause-card__actions-row">
              {clause.is_customized && (
                <Button
                  variant="ghost"
                  size="sm"
                  icon={RotateCcw}
                  onClick={() => onCustomize(clause, true)}
                >
                  Revert
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                icon={Pencil}
                onClick={() => onCustomize(clause, false)}
              >
                Customize with AI
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main ClausesStep ────────────────────────────────────────────────────────
export default function ClausesStep({
  contractId, contract, onContractUpdate, onNext, onPrev, markDone,
}) {
  const { showToast } = useToast();
  const [clauses, setClauses]             = useState([]);
  const [loading, setLoading]             = useState(true);
  const [generating, setGenerating]       = useState(false);
  const [defaultVariant, setDefaultVariant] = useState('Moderate');
  const [regenOpen, setRegenOpen]         = useState(false);

  // Customize modal
  const [customizeTarget, setCustomizeTarget] = useState(null);
  const [revertMode, setRevertMode]           = useState(false);
  const [instruction, setInstruction]         = useState('');
  const [customizeResult, setCustomizeResult] = useState(null);
  const [customizeLoading, setCustomizeLoading] = useState(false);
  const [applyLoading, setApplyLoading]       = useState(false);

  const loadClauses = useCallback(() => {
    setLoading(true);
    getActiveClauses(contractId)
      .then(setClauses)
      .catch(() => setClauses([]))
      .finally(() => setLoading(false));
  }, [contractId]);

  useEffect(() => { loadClauses(); }, [loadClauses]);

  // ── Generate (first time) ────────────────────────────────────────────────
  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generateClauses(contractId, defaultVariant);
      showToast('Clauses generated', 'success');
    } catch (err) {
      if (err.status === 400 && err.message?.toLowerCase().includes('already')) {
        showToast('Clauses already exist — loading them now', 'success');
      } else {
        showToast(err.message || 'Generation failed', 'error');
        setGenerating(false);
        return;
      }
    }
    loadClauses();
    setGenerating(false);
  };

  // ── Regenerate ──────────────────────────────────────────────────────────
  const handleRegenerate = async () => {
    setGenerating(true);
    try {
      await deleteAllClauses(contractId);
      await generateClauses(contractId, defaultVariant);
      showToast('Clauses regenerated', 'success');
      loadClauses();
      setRegenOpen(false);
    } catch (err) {
      showToast(err.message || 'Regeneration failed', 'error');
    } finally {
      setGenerating(false);
    }
  };

  // ── Customize modal handlers ────────────────────────────────────────────
  const openCustomize = (clause, inRevertMode) => {
    setCustomizeTarget(clause);
    setRevertMode(inRevertMode);
    setInstruction('');
    setCustomizeResult(null);
  };

  const handleCustomizeGenerate = async () => {
    setCustomizeLoading(true);
    try {
      const result = await customizeClause(contractId, customizeTarget.id, instruction);
      setCustomizeResult(result);
    } catch (err) {
      showToast(err.message || 'Customization failed', 'error');
    } finally {
      setCustomizeLoading(false);
    }
  };

  const handleApply = async () => {
    setApplyLoading(true);
    try {
      await applyCustomization(contractId, customizeTarget.id, customizeResult.customized_text);
      showToast('Customization applied', 'success');
      setCustomizeTarget(null);
      loadClauses();
    } catch (err) {
      showToast(err.message || 'Apply failed', 'error');
    } finally {
      setApplyLoading(false);
    }
  };

  const handleRevert = async () => {
    try {
      await revertCustomization(contractId, customizeTarget.id);
      showToast('Reverted to original', 'success');
      setCustomizeTarget(null);
      loadClauses();
    } catch (err) {
      showToast(err.message || 'Revert failed', 'error');
    }
  };

  const handleNext = () => {
    markDone('clauses');
    onNext();
  };

  // ── Risk summary ─────────────────────────────────────────────────────────
  const riskCounts = clauses.reduce((acc, c) => {
    const r = riskLevel(c.risk_level);
    if (r) acc[r] = (acc[r] ?? 0) + 1;
    return acc;
  }, {});

  if (loading) return <LoadingState />;

  return (
    <div className="clauses-step">

      {/* ── Empty / Generate-first hero ───────────────────────────────── */}
      {clauses.length === 0 ? (
        <div className="clauses-generate-hero">
          <div className="clauses-generate-hero__icon">
            <Sparkles size={24} strokeWidth={1.5} />
          </div>
          <div>
            <h3>Generate Your Clauses</h3>
            <p>
              LegalWiz will pull the right clauses from the knowledge graph for a{' '}
              <strong>{contract.contract_type.replace(/_/g, ' ')}</strong> under{' '}
              <strong>{contract.jurisdiction}</strong> law.
            </p>
          </div>
          <div className="clauses-generate-hero__controls">
            <Select
              options={VARIANT_OPTIONS}
              value={defaultVariant}
              onChange={(e) => setDefaultVariant(e.target.value)}
              label="Default Strictness"
              id="clause-variant-select"
            />
            <Button loading={generating} onClick={handleGenerate} size="lg">
              Generate Clauses
            </Button>
          </div>
        </div>
      ) : (
        <>
          {/* ── Toolbar ──────────────────────────────────────────────── */}
          <div className="clauses-toolbar">
            <div className="clauses-toolbar__left">
              <span className="clauses-toolbar__title">
                <ListOrdered size={15} strokeWidth={1.75} />
                {clauses.length} Active Clauses
              </span>
              <span className="clauses-toolbar__subtitle">
                Expand a clause to read its text or customize it with AI.
              </span>
            </div>
            <div className="clauses-toolbar__actions">
              <Button
                variant="ghost"
                size="sm"
                icon={RefreshCw}
                onClick={() => setRegenOpen(true)}
              >
                Regenerate
              </Button>
            </div>
          </div>

          {/* ── Risk legend ──────────────────────────────────────────── */}
          {Object.keys(riskCounts).length > 0 && (
            <div className="clauses-risk-legend">
              <span className="clauses-risk-legend__label">Risk</span>
              {['low', 'medium', 'high', 'critical'].map((r) =>
                riskCounts[r] ? (
                  <span key={r} className={`risk-dot risk-dot--${r}`}>
                    {riskCounts[r]} {r}
                  </span>
                ) : null
              )}
            </div>
          )}

          {/* ── Clause list ──────────────────────────────────────────── */}
          <div className="clauses-list">
            {clauses.map((clause) => (
              <ClauseCard
                key={clause.id || clause.clause_id}
                clause={clause}
                contractId={contractId}
                onRefresh={loadClauses}
                onCustomize={openCustomize}
              />
            ))}
          </div>
        </>
      )}

      {/* ── Step nav ─────────────────────────────────────────────────── */}
      <div className="step-nav">
        <Button variant="ghost" icon={ChevronLeft} onClick={onPrev}>Back</Button>
        <Button
          variant="primary"
          icon={ChevronRight}
          onClick={handleNext}
          disabled={clauses.length === 0}
          title={clauses.length === 0 ? 'Generate clauses first' : undefined}
        >
          Next: Fill Details
        </Button>
      </div>

      {/* ── Regenerate confirmation modal ─────────────────────────────── */}
      <Modal
        isOpen={regenOpen}
        onClose={() => setRegenOpen(false)}
        title="Regenerate Clauses"
        footer={
          <>
            <Button variant="ghost" onClick={() => setRegenOpen(false)}>Cancel</Button>
            <Button variant="danger" loading={generating} onClick={handleRegenerate}>
              Yes, Regenerate
            </Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          <p className="regen-warning">
            ⚠ This will delete all {clauses.length} existing clauses and any customizations.
            This cannot be undone.
          </p>
          <Select
            label="New Default Variant"
            options={VARIANT_OPTIONS}
            value={defaultVariant}
            onChange={(e) => setDefaultVariant(e.target.value)}
            id="regen-variant-select"
          />
        </div>
      </Modal>

      {/* ── Customize / Revert modal ──────────────────────────────────── */}
      <Modal
        isOpen={!!customizeTarget}
        onClose={() => { setCustomizeTarget(null); setCustomizeResult(null); }}
        title={
          revertMode
            ? `Revert: ${customizeTarget?.clause_type_name || customizeTarget?.clause_type || ''}`
            : `Customize: ${customizeTarget?.clause_type_name || customizeTarget?.clause_type || ''}`
        }
        size="lg"
        footer={
          <>
            <Button variant="ghost" onClick={() => { setCustomizeTarget(null); setCustomizeResult(null); }}>
              Close
            </Button>
            {revertMode ? (
              <Button variant="danger" onClick={handleRevert}>
                Revert to Original
              </Button>
            ) : (
              <>
                {customizeResult && (
                  <Button loading={applyLoading} onClick={handleApply}>
                    Apply Customization
                  </Button>
                )}
              </>
            )}
          </>
        }
      >
        {customizeTarget && (
          <div className="customize-modal">
            {/* Current text */}
            <div>
              <p className="customize-modal__section-label">Current Text</p>
              <pre className="customize-modal__pre">
                {customizeTarget.overridden_text || customizeTarget.raw_text || 'No text.'}
              </pre>
            </div>

            {/* Only show instruction + generate in customize mode */}
            {!revertMode && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
                <Textarea
                  label="Customization instruction"
                  value={instruction}
                  onChange={(e) => setInstruction(e.target.value)}
                  placeholder="e.g. Make the non-compete clause stricter and extend to 2 years"
                  rows={3}
                />
                <Button
                  icon={Sparkles}
                  loading={customizeLoading}
                  onClick={handleCustomizeGenerate}
                  disabled={!instruction.trim()}
                >
                  Generate Preview
                </Button>
              </div>
            )}

            {/* Customized result */}
            {customizeResult && (
              <div>
                <p className="customize-modal__section-label">Customized Text</p>
                <pre className="customize-modal__pre customize-modal__pre--new">
                  {customizeResult.customized_text}
                </pre>
                {customizeResult.risk_impact && (
                  <p className="customize-modal__risk-impact">
                    Risk impact: {customizeResult.risk_impact}
                  </p>
                )}
              </div>
            )}

            {/* Revert mode confirmation */}
            {revertMode && (
              <p className="regen-warning">
                This will remove your customization and restore the original clause text.
              </p>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
