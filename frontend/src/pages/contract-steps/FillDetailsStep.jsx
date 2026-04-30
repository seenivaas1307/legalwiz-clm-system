/**
 * FillDetailsStep — Step 4: Fill Contract Parameters
 *
 * Key improvements over ParametersTab:
 *  - Calls ?group_by=semantic → 13 semantic categories
 *  - Semantic group nav tabs (click to jump categories)
 *  - Progress bar (filled / total + %)
 *  - Auto-fill counter pills (auto, default, cascade, user, missing)
 *  - Provenance badge per field (auto_fill / system_default / cascade / user)
 *  - "Apply Smart Defaults" button at top
 *  - Cascade-on-change: date fields auto-derive related params
 *  - "All auto-filled" badge hides categories the user doesn't need to touch
 *  - Save + Validate with clear banner
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  FormInput, Zap, CheckCircle, AlertCircle,
  ChevronLeft, ChevronRight,
} from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Input from '../../components/common/Input.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { setParametersBulk, validateParameters } from '../../api/parameters.js';
import { getParametersGroupedSemantic, applySmartDefaults, cascadeParameter, autoFillFromParties } from '../../api/autofill.js';
import './FillDetailsStep.css';

// ── Provenance badge ─────────────────────────────────────────────────────────
const PROVENANCE_LABELS = {
  auto_fill:      'Auto-filled',
  system_default: 'Default',
  cascade:        'Derived',
  user:           'Edited',
};

function ProvenanceBadge({ source }) {
  if (!source) return null;
  return (
    <span className={`badge-provenance badge-provenance--${source}`}>
      {PROVENANCE_LABELS[source] ?? source}
    </span>
  );
}

// ── Semantic group nav button ────────────────────────────────────────────────
function GroupNavBtn({ group, isActive, onClick }) {
  const filled  = group.filled_count ?? 0;
  const total   = group.total_count  ?? group.parameters?.length ?? 0;
  const allDone = filled === total && total > 0;
  const allAuto = group.all_auto_filled;

  return (
    <button
      type="button"
      className={[
        'fill-group-btn',
        isActive  ? 'fill-group-btn--active' : '',
        allAuto   ? 'fill-group-btn--done'   : '',
      ].filter(Boolean).join(' ')}
      onClick={onClick}
    >
      {group.label}
      <span className="fill-group-btn__count">{total - filled || total}</span>
    </button>
  );
}

// ── Parameter input field ────────────────────────────────────────────────────
function ParamField({ param, value, onChange, onBlurCascade, cascading }) {
  const isUnfilled = value === '' || value == null;
  const fieldClass = [
    'fill-field',
    param.is_required && isUnfilled ? 'fill-field--required-unfilled' : '',
    cascading                        ? 'fill-field--cascading'         : '',
  ].filter(Boolean).join(' ');

  const inputType =
    param.data_type === 'date'    ? 'date'   :
    param.data_type === 'integer' ? 'number' :
    param.data_type === 'decimal' ? 'number' :
    'text';

  return (
    <div className={fieldClass} title={param.description || undefined}>
      <Input
        id={`param-${param.id}`}
        label={param.display_name || param.name}
        type={inputType}
        value={value ?? ''}
        onChange={(e) => onChange(param.id, e.target.value)}
        onBlur={onBlurCascade ? () => onBlurCascade(param.name, value) : undefined}
        placeholder={
          param.example_value
            ? `e.g. ${param.example_value}`
            : `Enter ${param.display_name || param.name}`
        }
        hint={param.description || undefined}
        required={param.is_required}
      />
      <div className="fill-field__meta">
        <ProvenanceBadge source={param.provided_by} />
      </div>
    </div>
  );
}

// ── Main component ──────────────────────────────────────────────────────────
export default function FillDetailsStep({
  contractId, contract, onNext, onPrev, markDone,
}) {
  const { showToast } = useToast();

  const [groups, setGroups]           = useState([]);
  const [summary, setSummary]         = useState({});
  const [values, setValues]           = useState({});           // paramId → value
  const [provenance, setProvenance]   = useState({});           // paramId → provided_by
  const [loading, setLoading]         = useState(true);
  const [saving, setSaving]           = useState(false);
  const [defaulting, setDefaulting]   = useState(false);
  const [autoFilling, setAutoFilling] = useState(false);
  const [cascading, setCascading]     = useState(new Set());    // param ids being cascaded
  const [validation, setValidation]   = useState(null);
  const [activeGroup, setActiveGroup] = useState(null);         // category key

  // ── Load semantic groups ─────────────────────────────────────────────────
  const loadParams = useCallback(async () => {
    setLoading(true);
    setValidation(null);
    try {
      const data = await getParametersGroupedSemantic(contractId);
      const g = data.groups ?? [];
      setGroups(g);
      setSummary({
        total:      data.total_parameters ?? 0,
        filled:     data.filled_parameters ?? 0,
        autoFilled: data.auto_filled_count ?? 0,
        defaulted:  data.defaulted_count ?? 0,
        cascaded:   data.cascade_filled_count ?? 0,
        remaining:  data.remaining_count ?? 0,
        pct:        data.completion_percentage ?? 0,
      });

      // Build flat lookup for values + provenance
      const vals = {};
      const prov = {};
      g.forEach((group) => {
        (group.parameters || []).forEach((p) => {
          if (p.current_value != null) vals[p.id] = String(p.current_value);
          prov[p.id] = p.provided_by ?? null;
        });
      });
      setValues(vals);
      setProvenance(prov);

      // Default active group to first with remaining params
      if (g.length > 0) {
        const firstUnfinished = g.find(
          (gr) => (gr.filled_count ?? 0) < (gr.total_count ?? gr.parameters?.length ?? 0)
        );
        setActiveGroup((firstUnfinished ?? g[0]).category);
      }
    } catch {
      setGroups([]);
    } finally {
      setLoading(false);
    }
  }, [contractId]);

  useEffect(() => { loadParams(); }, [loadParams]);

  // ── Field change ────────────────────────────────────────────────────────
  const handleChange = (paramId, value) => {
    setValues((v) => ({ ...v, [paramId]: value }));
    setProvenance((p) => ({ ...p, [paramId]: 'user' }));
    setValidation(null);
  };

  // ── Cascade on blur ─────────────────────────────────────────────────────
  const handleCascade = useCallback(async (paramName, value) => {
    if (!value) return;
    // Only cascade date-like params
    const bare = paramName.replace(/[{}]/g, '').toUpperCase();
    const isDate = ['DATE', 'TERM', 'PERIOD', 'DURATION', 'EXPIRY', 'RENEWAL'].some(
      (k) => bare.includes(k)
    );
    if (!isDate) return;

    try {
      const result = await cascadeParameter(contractId, paramName, value);
      if (result?.cascaded?.length > 0) {
        const newVals = { ...values };
        const newProv = { ...provenance };
        result.cascaded.forEach(({ param_id, value: cv }) => {
          newVals[param_id] = String(cv);
          newProv[param_id] = 'cascade';
        });
        setValues(newVals);
        setProvenance(newProv);
        showToast(`${result.cascaded.length} related field(s) derived`, 'success');
        // Reload groups to update counts
        const data = await getParametersGroupedSemantic(contractId);
        setGroups(data.groups ?? []);
        setSummary({
          total:      data.total_parameters ?? 0,
          filled:     data.filled_parameters ?? 0,
          autoFilled: data.auto_filled_count ?? 0,
          defaulted:  data.defaulted_count ?? 0,
          cascaded:   data.cascade_filled_count ?? 0,
          remaining:  data.remaining_count ?? 0,
          pct:        data.completion_percentage ?? 0,
        });
      }
    } catch { /* silent — cascade is best-effort */ }
  }, [contractId, values, provenance]);

  // ── Auto-fill from parties ────────────────────────────────────────────────
  const handleAutoFillFromParties = async () => {
    setAutoFilling(true);
    try {
      const result = await autoFillFromParties(contractId);
      const count = result.auto_filled ?? 0;
      showToast(
        count > 0
          ? `Auto-filled ${count} parameters from party data`
          : (result.message || 'No matching parameters found for party data'),
        count > 0 ? 'success' : 'info'
      );
      await loadParams();
    } catch (err) {
      showToast(err.message || 'Auto-fill failed', 'error');
    } finally {
      setAutoFilling(false);
    }
  };

  // ── Apply smart defaults ─────────────────────────────────────────────────
  const handleDefaults = async () => {
    setDefaulting(true);
    try {
      const result = await applySmartDefaults(contractId);
      showToast(
        `${result.defaults_applied ?? result.applied_count ?? 0} defaults applied`,
        'success'
      );
      await loadParams();
    } catch (err) {
      showToast(err.message || 'Defaults failed', 'error');
    } finally {
      setDefaulting(false);
    }
  };

  // ── Save all ────────────────────────────────────────────────────────────
  const handleSave = async () => {
    setSaving(true);
    try {
      const params = Object.entries(values)
        .filter(([, v]) => v !== '' && v != null)
        .map(([parameter_id, value]) => ({ parameter_id, value }));
      await setParametersBulk(contractId, params);
      showToast('Parameters saved', 'success');
      const result = await validateParameters(contractId);
      setValidation(result);
      await loadParams();
    } catch (err) {
      showToast(err.message || 'Save failed', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleNext = () => {
    markDone('fill');
    onNext();
  };

  // ── Derived state ────────────────────────────────────────────────────────
  const activeGroupData = groups.find((g) => g.category === activeGroup);
  const allParams = groups.flatMap((g) => g.parameters ?? []);

  // ── Edge cases ──────────────────────────────────────────────────────────
  if (loading) return <LoadingState message="Loading parameters…" />;

  if (allParams.length === 0) {
    return (
      <div className="fill-step">
        <EmptyState
          title="No parameters yet"
          description="Generate clauses first. Parameters are extracted from clause placeholders."
        />
        <div className="step-nav">
          <Button variant="ghost" icon={ChevronLeft} onClick={onPrev}>Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="fill-step">

      {/* ── Toolbar ────────────────────────────────────────────────────── */}
      <div className="fill-toolbar">
        <div className="fill-toolbar__left">
          <span className="fill-toolbar__heading">
            <FormInput size={15} strokeWidth={1.75} />
            Fill Contract Details
          </span>
          <span className="fill-toolbar__sub">
            {summary.remaining > 0
              ? `${summary.remaining} of ${summary.total} fields still need your input.`
              : `All ${summary.total} fields are filled — ready to review.`}
          </span>
        </div>
        <div className="fill-toolbar__actions">
          <Button
            variant="ghost"
            size="sm"
            icon={Zap}
            loading={autoFilling}
            onClick={handleAutoFillFromParties}
            title="Map party data (names, addresses) to contract parameters"
          >
            Auto-Fill from Parties
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon={Zap}
            loading={defaulting}
            onClick={handleDefaults}
            title="Apply jurisdiction-aware smart defaults"
          >
            Smart Defaults
          </Button>
          <Button
            variant="secondary"
            size="sm"
            loading={saving}
            onClick={handleSave}
          >
            Save
          </Button>
        </div>
      </div>

      {/* ── Progress bar ────────────────────────────────────────────────── */}
      <div className="fill-progress">
        <div className="fill-progress__bar">
          <div
            className="fill-progress__fill"
            style={{ width: `${Math.max(summary.pct ?? 0, 2)}%` }}
          />
        </div>
        <span className="fill-progress__pct">{summary.pct ?? 0}%</span>
      </div>

      {/* ── Auto-fill summary pills ─────────────────────────────────────── */}
      {(summary.autoFilled > 0 || summary.defaulted > 0 || summary.cascaded > 0) && (
        <div className="fill-autofill-strip">
          {summary.autoFilled > 0 && (
            <span className="fill-counter fill-counter--auto">
              ⬤ {summary.autoFilled} auto-filled from parties
            </span>
          )}
          {summary.defaulted > 0 && (
            <span className="fill-counter fill-counter--default">
              ⬤ {summary.defaulted} smart defaults applied
            </span>
          )}
          {summary.cascaded > 0 && (
            <span className="fill-counter fill-counter--cascade">
              ⬤ {summary.cascaded} derived from other fields
            </span>
          )}
          {summary.remaining > 0 && (
            <span className="fill-counter fill-counter--missing">
              ⬤ {summary.remaining} still needed
            </span>
          )}
        </div>
      )}

      {/* ── Validation banner ────────────────────────────────────────────── */}
      {validation && (
        <div className={`fill-validation fill-validation--${validation.is_valid ? 'valid' : 'invalid'}`}>
          {validation.is_valid ? (
            <><CheckCircle size={16} /> All required parameters are filled.</>
          ) : (
            <>
              <AlertCircle size={16} />
              <span>
                {validation.missing_count} parameter(s) still needed:&nbsp;
                <strong>{(validation.missing_parameters || []).join(', ')}</strong>
              </span>
            </>
          )}
        </div>
      )}

      {/* ── Group nav tabs ──────────────────────────────────────────────── */}
      <div className="fill-group-nav" role="tablist">
        {groups.map((group) => (
          <GroupNavBtn
            key={group.category}
            group={group}
            isActive={group.category === activeGroup}
            onClick={() => setActiveGroup(group.category)}
          />
        ))}
      </div>

      {/* ── Active category fields ──────────────────────────────────────── */}
      {activeGroupData && (
        <>
          <div className="fill-category-heading">
            <div className="fill-category-heading__left">
              <span>{activeGroupData.label}</span>
              <span className={`fill-category-badge ${activeGroupData.all_auto_filled ? 'fill-category-badge--complete' : ''}`}>
                {activeGroupData.filled_count ?? 0} / {activeGroupData.total_count ?? activeGroupData.parameters?.length ?? 0} filled
              </span>
            </div>
            {activeGroupData.all_auto_filled && (
              <span className="fill-all-auto-badge">
                <CheckCircle size={12} /> All auto-filled
              </span>
            )}
          </div>

          <div className="fill-fields">
            {(activeGroupData.parameters ?? []).map((param) => (
              <ParamField
                key={param.id}
                param={{ ...param, provided_by: provenance[param.id] ?? param.provided_by }}
                value={values[param.id] ?? ''}
                onChange={handleChange}
                onBlurCascade={handleCascade}
                cascading={cascading.has(param.id)}
              />
            ))}
          </div>
        </>
      )}

      {/* ── Step nav ─────────────────────────────────────────────────────── */}
      <div className="step-nav">
        <Button variant="ghost" icon={ChevronLeft} onClick={onPrev}>Back</Button>
        <div style={{ display: 'flex', gap: 'var(--sp-2)' }}>
          <Button variant="secondary" loading={saving} onClick={handleSave}>
            Save
          </Button>
          <Button variant="primary" icon={ChevronRight} onClick={handleNext}>
            Next: Review
          </Button>
        </div>
      </div>
    </div>
  );
}
