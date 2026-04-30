import { riskColor, riskLabel } from '../../utils/date.js';
import './RiskIndicator.css';

export default function RiskIndicator({ score, size = 'md' }) {
  const color = riskColor(score);
  const label = riskLabel(score);
  const s = parseFloat(score) || 0;

  return (
    <span className={`risk-indicator risk-indicator--${size}`} style={{ color }}>
      <span className="risk-indicator__score">{s.toFixed(1)}</span>
      <span className="risk-indicator__label">{label}</span>
    </span>
  );
}
