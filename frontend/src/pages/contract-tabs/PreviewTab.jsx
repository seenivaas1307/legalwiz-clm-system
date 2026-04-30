import { useState, useEffect, useCallback } from 'react';
import { AlertTriangle, Eye, RefreshCw } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import { previewContract } from '../../api/export.js';
import { parsePlaceholders } from '../../utils/date.js';
import './PreviewTab.css';

function ClauseText({ text }) {
  const segments = parsePlaceholders(text);
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

export default function PreviewTab({ contractId, onFillParams }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const loadPreview = useCallback(() => {
    setLoading(true);
    previewContract(contractId)
      .then((d) => { setData(d); setLoaded(true); })
      .catch(() => { setLoaded(true); setData(null); })
      .finally(() => setLoading(false));
  }, [contractId]);

  // Reload every time the tab is shown (component mounts)
  useEffect(() => { loadPreview(); }, [loadPreview]);

  if (loading) return <LoadingState message="Assembling contract preview..." />;

  if (!loaded || !data) {
    return (
      <EmptyState
        icon={Eye}
        title="Preview unavailable"
        description="Generate clauses first to preview the assembled contract."
      />
    );
  }

  const { contract, clauses, parameters, missing_parameters, is_complete, word_count } = data;

  return (
    <div className="preview-tab">
      {/* Refresh button */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--sp-3)' }}>
        <Button variant="ghost" size="sm" icon={RefreshCw} onClick={loadPreview} loading={loading}>
          Refresh Preview
        </Button>
      </div>

      {/* Missing parameters alert */}
      {!is_complete && missing_parameters && missing_parameters.length > 0 && (
        <div className="preview-alert">
          <AlertTriangle size={16} strokeWidth={1.75} className="preview-alert__icon" />
          <div className="preview-alert__content">
            <strong>{missing_parameters.length} parameter{missing_parameters.length !== 1 ? 's' : ''} need to be filled</strong>
            <div className="preview-alert__list">
              {missing_parameters.map((p) => (
                <span key={p.parameter_id || p} className="text-mono preview-alert__param">
                  {p.parameter_name || p}
                </span>
              ))}
            </div>
          </div>
          <Button size="sm" onClick={onFillParams}>Fill Parameters</Button>
        </div>
      )}

      {/* Contract document */}
      <div className="preview-document">
        <div className="preview-document__cover">
          <h2 className="preview-document__title">{contract?.title}</h2>
          <p className="preview-document__meta">
            {contract?.contract_type} &bull; {contract?.jurisdiction}
          </p>
          <hr className="preview-document__divider" />
        </div>

        <div className="preview-document__body">
          {(clauses || []).map((clause, idx) => (
            <div key={clause.id || idx} className="preview-clause">
              <div className="preview-clause__header">
                <span className="preview-clause__num">{idx + 1}.</span>
                <span className="preview-clause__type">{clause.clause_type_name || clause.clause_type}</span>
              </div>
              <div className="preview-clause__text">
                <ClauseText text={clause.rendered_text || clause.text || clause.raw_text || clause.overridden_text || ''} />
              </div>
              {idx < (clauses.length - 1) && <hr className="preview-clause__sep" />}
            </div>
          ))}
        </div>

        <div className="preview-document__footer">
          <span className="preview-document__end">-- End of Contract --</span>
          {word_count && (
            <span className="preview-document__wordcount">{word_count.toLocaleString()} words</span>
          )}
        </div>
      </div>

      {is_complete && (
        <div className="preview-complete">
          All parameters have been filled. This contract is ready for export.
        </div>
      )}
    </div>
  );
}
