import { STATUS_LABELS } from '../../utils/labels.js';
import './StatusBadge.css';

const STATUS_COLORS = {
  draft: 'var(--status-draft)',
  in_review: 'var(--status-in-review)',
  approved: 'var(--status-approved)',
  signed: 'var(--status-signed)',
  active: 'var(--status-active)',
  terminated: 'var(--status-terminated)',
};

export default function StatusBadge({ status }) {
  const color = STATUS_COLORS[status] || 'var(--ink-ghost)';
  const label = STATUS_LABELS[status] || status;

  return (
    <span className="status-badge">
      <span className="status-badge__dot" style={{ background: color }} />
      <span className="status-badge__label">{label}</span>
    </span>
  );
}
