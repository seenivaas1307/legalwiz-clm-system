import { useState, useEffect, useCallback } from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Input from '../../components/common/Input.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { getParametersGrouped, setParametersBulk, validateParameters } from '../../api/parameters.js';
import './ParametersTab.css';

export default function ParametersTab({ contractId, onGoToPreview }) {
  const { showToast } = useToast();
  const [groups, setGroups] = useState([]);
  const [values, setValues] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validation, setValidation] = useState(null);

  const loadParams = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getParametersGrouped(contractId, 'display');
      const grouped = data.grouped || [];
      setGroups(grouped);
      // Flatten existing values
      const vals = {};
      grouped.forEach((group) => {
        (group.parameters || []).forEach((p) => {
          if (p.current_value !== null && p.current_value !== undefined) {
            vals[p.parameter_id] = p.current_value;
          }
        });
      });
      setValues(vals);
    } catch {
      setGroups([]);
    } finally {
      setLoading(false);
    }
  }, [contractId]);

  useEffect(() => { loadParams(); }, [loadParams]);

  const handleChange = (parameterId, value) => {
    setValues((v) => ({ ...v, [parameterId]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const params = Object.entries(values)
        .filter(([, v]) => v !== '' && v !== null && v !== undefined)
        .map(([parameter_id, value]) => ({ parameter_id, value }));
      await setParametersBulk(contractId, params);
      showToast('Parameters saved', 'success');
      // Validate
      const result = await validateParameters(contractId);
      setValidation(result);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState message="Loading parameters..." />;

  const allParams = groups.flatMap((g) => g.parameters || []);
  if (allParams.length === 0) {
    return (
      <EmptyState
        title="No parameters found"
        description="Generate clauses first. Parameters are extracted from clause placeholders."
      />
    );
  }

  return (
    <div className="parameters-tab">
      <div className="parameters-header">
        <div>
          <h3>Contract Parameters</h3>
          <p>Fill in the values below to replace all placeholders in the contract. The Preview tab will reflect these changes.</p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--sp-3)' }}>
          <Button loading={saving} onClick={handleSave}>Save All</Button>
          <Button variant="secondary" onClick={onGoToPreview}>View Preview</Button>
        </div>
      </div>

      {/* Validation result */}
      {validation && (
        <div className={`param-validation param-validation--${validation.is_valid ? 'valid' : 'invalid'}`}>
          {validation.is_valid
            ? <><CheckCircle size={16} /> All parameters filled correctly.</>
            : <><AlertCircle size={16} /> {validation.missing_count} parameter(s) still needed: {(validation.missing_parameters || []).join(', ')}</>
          }
        </div>
      )}

      {/* Parameter groups */}
      <div className="parameters-groups">
        {groups.map((group) => (
          <div key={group.group_name || group.clause_type} className="param-group">
            <h4 className="param-group__title">{group.group_name || group.clause_type}</h4>
            <div className="param-group__fields">
              {(group.parameters || []).map((param) => (
                <div key={param.parameter_id} className="param-field" title={param.description || `Parameter: ${param.display_name || param.parameter_id}`}>
                  <Input
                    id={`param-${param.parameter_id}`}
                    label={param.display_name || param.parameter_id}
                    value={values[param.parameter_id] || ''}
                    onChange={(e) => handleChange(param.parameter_id, e.target.value)}
                    placeholder={
                      param.example_value
                        ? `e.g. ${param.example_value}`
                        : param.display_name || param.parameter_id
                    }
                    hint={param.description}
                    required={param.is_required}
                  />
                  {!values[param.parameter_id] && (
                    <span className="param-field__unfilled">
                      Placeholder: <code>{param.placeholder_text || `{{${param.parameter_id}}}`}</code>
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="parameters-footer">
        <Button loading={saving} onClick={handleSave} size="lg">Save All Parameters</Button>
        <Button variant="secondary" onClick={onGoToPreview}>View in Preview</Button>
      </div>
    </div>
  );
}
