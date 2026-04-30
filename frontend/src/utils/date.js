export function formatDate(dateStr) {
  if (!dateStr) return '--';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(dateStr) {
  if (!dateStr) return '--';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function timeAgo(dateStr) {
  if (!dateStr) return '--';
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 30) return `${diffDays}d ago`;
  return formatDate(dateStr);
}

export function riskColor(score) {
  const s = parseFloat(score) || 0;
  if (s <= 3.5) return 'var(--risk-low)';
  if (s <= 5.5) return 'var(--risk-medium)';
  if (s <= 7.5) return 'var(--risk-high)';
  return 'var(--risk-critical)';
}

export function riskLabel(score) {
  const s = parseFloat(score) || 0;
  if (s <= 3.5) return 'Low';
  if (s <= 5.5) return 'Medium';
  if (s <= 7.5) return 'High';
  return 'Critical';
}

/**
 * Splits clause text by {{PLACEHOLDER}} patterns and returns an array
 * of { type: 'text'|'placeholder', content: string } segments.
 */
export function parsePlaceholders(text) {
  if (!text) return [];
  const parts = text.split(/({{[A-Z_0-9]+}})/g);
  return parts.map((part) => ({
    type: /^{{[A-Z_0-9]+}}$/.test(part) ? 'placeholder' : 'text',
    content: part,
  }));
}
