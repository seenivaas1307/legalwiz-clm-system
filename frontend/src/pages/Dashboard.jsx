import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, FileText } from 'lucide-react';
import AppShell from '../components/layout/AppShell.jsx';
import StatusBadge from '../components/common/StatusBadge.jsx';
import Button from '../components/common/Button.jsx';
import DataTable from '../components/common/DataTable.jsx';
import LoadingState from '../components/common/LoadingState.jsx';
import EmptyState from '../components/common/EmptyState.jsx';
import { listContracts } from '../api/contracts.js';
import { CONTRACT_TYPE_LABELS } from '../utils/labels.js';
import { timeAgo } from '../utils/date.js';
import './Dashboard.css';

const METRIC_CARDS = [
  { label: 'Total Contracts', key: 'total' },
  { label: 'Active', key: 'active' },
  { label: 'In Review', key: 'inReview' },
  { label: 'Drafts', key: 'drafts' },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listContracts({ limit: 100 })
      .then(setContracts)
      .catch(() => setContracts([]))
      .finally(() => setLoading(false));
  }, []);

  const metrics = {
    total: contracts.length,
    active: contracts.filter((c) => ['active', 'signed', 'approved'].includes(c.status)).length,
    inReview: contracts.filter((c) => c.status === 'in_review').length,
    drafts: contracts.filter((c) => c.status === 'draft').length,
  };

  const recent = [...contracts]
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    .slice(0, 10);

  const columns = [
    {
      key: 'title',
      label: 'Title',
      render: (val, row) => (
        <span className="table-title">{val}</span>
      ),
    },
    {
      key: 'contract_type',
      label: 'Type',
      render: (val) => (
        <span className="text-mono" style={{ color: 'var(--ink-tertiary)' }}>
          {CONTRACT_TYPE_LABELS[val] || val}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: 'jurisdiction',
      label: 'Jurisdiction',
      render: (val) => <span style={{ color: 'var(--ink-secondary)' }}>{val}</span>,
    },
    {
      key: 'updated_at',
      label: 'Updated',
      render: (val) => <span style={{ color: 'var(--ink-tertiary)', fontSize: '0.8125rem' }}>{timeAgo(val)}</span>,
    },
  ];

  return (
    <AppShell pageTitle="Dashboard">
      <div className="dashboard">
        <div className="dashboard__header">
          <h1>Dashboard</h1>
        </div>

        {loading ? (
          <LoadingState />
        ) : (
          <>
            {/* Metric cards */}
            <div className="dashboard__metrics">
              {METRIC_CARDS.map((card) => (
                <div key={card.key} className="metric-card">
                  <h4>{card.label}</h4>
                  <span className="metric-card__number">{metrics[card.key]}</span>
                </div>
              ))}
            </div>

            {/* Recent contracts */}
            <div className="dashboard__recent">
              <div className="section-header">
                <h3>Recent Contracts</h3>
                <Button
                  variant="primary"
                  size="sm"
                  icon={Plus}
                  onClick={() => navigate('/contracts/new')}
                >
                  New Contract
                </Button>
              </div>

              {recent.length === 0 ? (
                <EmptyState
                  icon={FileText}
                  title="No contracts yet"
                  description="Create your first contract to get started with LegalWiz."
                  action={
                    <Button icon={Plus} onClick={() => navigate('/contracts/new')}>
                      New Contract
                    </Button>
                  }
                />
              ) : (
                <DataTable
                  columns={columns}
                  data={recent}
                  onRowClick={(row) => navigate(`/contracts/${row.id}`)}
                />
              )}
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
