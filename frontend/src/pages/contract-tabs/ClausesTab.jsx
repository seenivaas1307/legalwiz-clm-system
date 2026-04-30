import { useState, useEffect, useCallback } from 'react';
import { ChevronDown, ChevronUp, RefreshCw, Pencil, FileText, Trash2 } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Select from '../../components/common/Select.jsx';
import Modal from '../../components/common/Modal.jsx';
import Textarea from '../../components/common/Textarea.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { getActiveClauses, generateClauses, switchVariant, deleteAllClauses } from '../../api/clauses.js';
import { customizeClause, applyCustomization, revertCustomization } from '../../api/customization.js';
import { riskColor } from '../../utils/date.js';
import { VARIANT_OPTIONS } from '../../utils/labels.js';
import './ClausesTab.css';

function ClauseItem({ clause, contractId, onRefresh, onCustomize }) {
  const [expanded, setExpanded] = useState(false);
  const [switching, setSwitching] = useState(false);
  const { showToast } = useToast();

  const handleVariantChange = async (e) => {
    const newVariant = e.target.value;
    if (newVariant === clause.variant) return;
    setSwitching(true);
    try {
      await switchVariant(contractId, clause.clause_type, newVariant);
      showToast(`Switched to ${newVariant} variant`, 'success');
      onRefresh();
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setSwitching(false); }
  };

  const text = clause.is_customized && clause.overridden_text
    ? clause.overridden_text
    : clause.raw_text;

  const availableVariants = (clause.available_variants || [])
    .filter((v) => v.is_active !== undefined)
    .map((v) => ({ value: v.variant, label: v.variant }));

  const riskBorderColor = clause.risk_level != null
    ? riskColor(clause.risk_level * 10)
    : 'var(--border-hairline)';

  return (
    <div className="clause-item" style={{ borderLeftColor: riskBorderColor }}>
      <div className="clause-item__header">
        <div className="clause-item__meta">
          <span className="clause-item__name">{clause.clause_type_name || clause.clause_type}</span>
          <span className="clause-item__id text-mono">{clause.clause_id}</span>
          {clause.is_customized && <span className="clause-item__custom-badge">Customized</span>}
          {clause.is_mandatory && <span className="clause-item__mandatory">Required</span>}
        </div>
        <div className="clause-item__controls">
          {availableVariants.length > 1 && (
            <select
              className="clause-item__variant-select"
              value={clause.variant}
              onChange={handleVariantChange}
              disabled={switching}
            >
              {availableVariants.map((v) => (
                <option key={v.value} value={v.value}>{v.label}</option>
              ))}
            </select>
          )}
          <Button variant="ghost" size="sm" icon={Pencil} onClick={() => onCustomize(clause)}>
            Customize
          </Button>
          <button
            className="clause-item__expand-btn"
            onClick={() => setExpanded((e) => !e)}
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>
      {expanded && (
        <div className="clause-item__body">
          <pre className="clause-item__text">{text || 'No text available.'}</pre>
        </div>
      )}
    </div>
  );
}

export default function ClausesTab({ contractId, onGoToPreview }) {
  const { showToast } = useToast();
  const [clauses, setClauses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [defaultVariant, setDefaultVariant] = useState('Moderate');
  const [regenConfirm, setRegenConfirm] = useState(false);

  // Customize modal state
  const [customizeClauseData, setCustomizeClauseData] = useState(null);
  const [instruction, setInstruction] = useState('');
  const [customizeResult, setCustomizeResult] = useState(null);
  const [customizeLoading, setCustomizeLoading] = useState(false);
  const [applyLoading, setApplyLoading] = useState(false);

  const loadClauses = useCallback(() => {
    setLoading(true);
    getActiveClauses(contractId)
      .then(setClauses)
      .catch(() => setClauses([]))
      .finally(() => setLoading(false));
  }, [contractId]);

  useEffect(() => { loadClauses(); }, [loadClauses]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generateClauses(contractId, defaultVariant);
      showToast('Clauses generated', 'success');
    } catch (err) {
      // 400 = clauses already exist — still load them, don't treat as fatal
      if (err.status === 400 && err.message?.toLowerCase().includes('already')) {
        showToast('Clauses already exist — loading them now', 'success');
      } else {
        showToast(err.message, 'error');
        setGenerating(false);
        return; // real error — don't try to load
      }
    }
    // Always reload after generate attempt (success OR already-exists)
    loadClauses();
    setGenerating(false);
  };

  const handleRegenerate = async () => {
    setGenerating(true);
    try {
      await deleteAllClauses(contractId);
      await generateClauses(contractId, defaultVariant);
      showToast('Clauses regenerated', 'success');
      loadClauses();
      setRegenConfirm(false);
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setGenerating(false); }
  };

  const openCustomize = (clause) => {
    setCustomizeClauseData(clause);
    setInstruction('');
    setCustomizeResult(null);
  };

  const handleCustomizeGenerate = async () => {
    setCustomizeLoading(true);
    try {
      const result = await customizeClause(contractId, customizeClauseData.id, instruction);
      setCustomizeResult(result);
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setCustomizeLoading(false); }
  };

  const handleApplyCustomization = async () => {
    setApplyLoading(true);
    try {
      await applyCustomization(contractId, customizeClauseData.id, customizeResult.customized_text);
      showToast('Customization applied', 'success');
      setCustomizeClauseData(null);
      loadClauses();
    } catch (err) {
      showToast(err.message, 'error');
    } finally { setApplyLoading(false); }
  };

  const handleRevert = async () => {
    try {
      await revertCustomization(contractId, customizeClauseData.id);
      showToast('Reverted to original', 'success');
      setCustomizeClauseData(null);
      loadClauses();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div className="clauses-tab">
      {clauses.length === 0 ? (
        <div className="clauses-empty">
          <EmptyState
            icon={FileText}
            title="No clauses generated yet"
            description="Generate clauses from the knowledge graph to begin building your contract."
          />
          <div className="clauses-empty__controls">
            <Select
              options={VARIANT_OPTIONS}
              value={defaultVariant}
              onChange={(e) => setDefaultVariant(e.target.value)}
              label="Default Variant"
              id="clause-variant"
            />
            <Button loading={generating} onClick={handleGenerate} size="lg">
              Generate Clauses
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="clauses-header">
            <div>
              <h3>{clauses.length} Active Clauses</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--ink-tertiary)', marginTop: 'var(--sp-1)', marginBottom: 0 }}>
                Click a clause to expand its full text. Use the variant selector to switch between Standard, Moderate, and Strict.
              </p>
            </div>
            <div style={{ display: 'flex', gap: 'var(--sp-3)', alignItems: 'center' }}>
              <Button variant="secondary" size="sm" icon={RefreshCw} onClick={() => setRegenConfirm(true)}>
                Regenerate
              </Button>
              <Button variant="primary" size="sm" onClick={onGoToPreview}>
                Preview Contract
              </Button>
            </div>
          </div>

          <div className="clauses-list">
            {clauses.map((clause) => (
              <ClauseItem
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

      {/* Regenerate confirmation */}
      <Modal
        isOpen={regenConfirm}
        onClose={() => setRegenConfirm(false)}
        title="Regenerate Clauses"
        footer={
          <>
            <Button variant="ghost" onClick={() => setRegenConfirm(false)}>Cancel</Button>
            <Button variant="danger" loading={generating} onClick={handleRegenerate}>Regenerate</Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-4)' }}>
          <p>This will delete all existing clauses and regenerate them. Any customizations will be lost.</p>
          <Select
            label="Default Variant"
            options={VARIANT_OPTIONS}
            value={defaultVariant}
            onChange={(e) => setDefaultVariant(e.target.value)}
            id="regen-variant"
          />
        </div>
      </Modal>

      {/* Customize modal */}
      <Modal
        isOpen={!!customizeClauseData}
        onClose={() => { setCustomizeClauseData(null); setCustomizeResult(null); }}
        title={`Customize: ${customizeClauseData?.clause_type_name || customizeClauseData?.clause_type || ''}`}
        size="lg"
        footer={
          <>
            <Button variant="ghost" onClick={() => { setCustomizeClauseData(null); setCustomizeResult(null); }}>Close</Button>
            {customizeClauseData?.is_customized && (
              <Button variant="secondary" onClick={handleRevert}>Revert to Original</Button>
            )}
            {customizeResult && (
              <Button loading={applyLoading} onClick={handleApplyCustomization}>Apply Customization</Button>
            )}
          </>
        }
      >
        {customizeClauseData && (
          <div className="customize-modal">
            <div className="customize-modal__original">
              <h4>Current Text</h4>
              <pre className="customize-modal__text">
                {customizeClauseData.overridden_text || customizeClauseData.raw_text || 'Loading...'}
              </pre>
            </div>

            <div className="customize-modal__instruction">
              <Textarea
                label="Customization instruction"
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                placeholder="e.g. Make the non-compete clause stricter and extend the duration to 2 years"
                rows={3}
              />
              <Button loading={customizeLoading} onClick={handleCustomizeGenerate} disabled={!instruction.trim()}>
                Generate Customization
              </Button>
            </div>

            {customizeResult && (
              <div className="customize-modal__result">
                <h4>Customized Text</h4>
                <pre className="customize-modal__text customize-modal__text--new">{customizeResult.customized_text}</pre>
                {customizeResult.risk_impact && (
                  <p style={{ fontSize: '0.8125rem', color: 'var(--ink-tertiary)', marginBottom: 0 }}>
                    Risk impact: {customizeResult.risk_impact}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
