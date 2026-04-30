import { useState, useEffect, useCallback } from 'react';
import { Lightbulb, AlertTriangle, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import RiskIndicator from '../../components/common/RiskIndicator.jsx';
import { getFullRiskAnalysis } from '../../api/risk.js';
import { getRecommendations } from '../../api/recommendations.js';
import { riskColor, riskLabel } from '../../utils/date.js';
import './InsightsTab.css';

function RiskItem({ item }) {
  const [open, setOpen] = useState(false);
  const color = riskColor(item.severity_score || item.severity);

  return (
    <div className="risk-item" style={{ borderLeftColor: color }}>
      <button className="risk-item__header" onClick={() => setOpen((o) => !o)}>
        <span className="risk-item__title">{item.clause_type || item.issue_type}</span>
        <span className="risk-item__meta">
          <span style={{ color, fontSize: '0.75rem', fontWeight: 600 }}>
            {riskLabel(item.severity_score || item.severity)}
          </span>
        </span>
        {open ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>
      {open && (
        <div className="risk-item__body">
          {item.issue && <p className="risk-item__text"><strong>Issue:</strong> {item.issue}</p>}
          {item.impact && <p className="risk-item__text"><strong>Impact:</strong> {item.impact}</p>}
          {item.recommendation && <p className="risk-item__text"><strong>Recommendation:</strong> {item.recommendation}</p>}
        </div>
      )}
    </div>
  );
}

function RecItem({ item }) {
  return (
    <div className="rec-item">
      <div className="rec-item__header">
        <span className="rec-item__type">{item.recommendation_type}</span>
        <span className="rec-item__clause">{item.clause_type}</span>
        {item.priority && <span className="rec-item__priority text-mono">{item.priority}</span>}
      </div>
      <p className="rec-item__reason">{item.reason}</p>
    </div>
  );
}

export default function InsightsTab({ contractId }) {
  const [risk, setRisk] = useState(null);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([
      getFullRiskAnalysis(contractId).catch(() => null),
      getRecommendations(contractId).catch(() => []),
    ]).then(([riskData, recData]) => {
      setRisk(riskData);
      setRecs(Array.isArray(recData) ? recData : recData?.recommendations || []);
      setLoaded(true);
    }).finally(() => setLoading(false));
  }, [contractId]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <LoadingState message="Running AI analysis..." />;

  if (!loaded) return (
    <EmptyState icon={Lightbulb} title="AI Insights" description="Click below to run risk analysis and get AI recommendations." action={
      <Button onClick={load}>Run Analysis</Button>
    } />
  );

  const riskItems = risk?.risk_items || risk?.risks || [];
  const overallScore = risk?.overall_risk_score || risk?.risk_score || null;

  return (
    <div className="insights-tab">
      <div className="insights-actions">
        <Button variant="ghost" size="sm" icon={RefreshCw} onClick={load}>Refresh</Button>
      </div>

      {/* Risk summary */}
      <div className="insights-section">
        <div className="insights-section__header">
          <h3>Risk Analysis</h3>
          {overallScore != null && <RiskIndicator score={overallScore} size="md" />}
        </div>

        {risk?.executive_summary && (
          <p className="insights-summary">{risk.executive_summary}</p>
        )}

        {riskItems.length === 0 ? (
          <p style={{ color: 'var(--ink-tertiary)', fontSize: '0.875rem' }}>No risk items identified.</p>
        ) : (
          <div className="risk-list">
            {riskItems.map((item, idx) => <RiskItem key={idx} item={item} />)}
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="insights-section">
        <h3 className="insights-section__header">AI Recommendations</h3>
        {recs.length === 0 ? (
          <p style={{ color: 'var(--ink-tertiary)', fontSize: '0.875rem' }}>No recommendations at this time.</p>
        ) : (
          <div className="rec-list">
            {recs.map((rec, idx) => <RecItem key={idx} item={rec} />)}
          </div>
        )}
      </div>
    </div>
  );
}
