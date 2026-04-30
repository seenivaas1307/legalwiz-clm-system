import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, FileText, Search } from 'lucide-react';
import AppShell from '../components/layout/AppShell.jsx';
import DataTable from '../components/common/DataTable.jsx';
import StatusBadge from '../components/common/StatusBadge.jsx';
import Button from '../components/common/Button.jsx';
import Input from '../components/common/Input.jsx';
import Select from '../components/common/Select.jsx';
import EmptyState from '../components/common/EmptyState.jsx';
import LoadingState from '../components/common/LoadingState.jsx';
import { listContracts } from '../api/contracts.js';
import { CONTRACT_TYPE_OPTIONS, STATUS_OPTIONS, CONTRACT_TYPE_LABELS } from '../utils/labels.js';
import { formatDate } from '../utils/date.js';
import './ContractList.css';

export default function ContractList() {
  const navigate = useNavigate();
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    listContracts({ limit: 200 })
      .then(setContracts)
      .catch(() => setContracts([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = contracts.filter((c) => {
    const matchesSearch = !search || c.title.toLowerCase().includes(search.toLowerCase());
    const matchesType = !typeFilter || c.contract_type === typeFilter;
    const matchesStatus = !statusFilter || c.status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const columns = [
    {
      key: 'title',
      label: 'Title',
      render: (val) => <span className="table-title">{val}</span>,
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
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (val) => <span style={{ color: 'var(--ink-tertiary)', fontSize: '0.8125rem' }}>{formatDate(val)}</span>,
    },
  ];

  return (
    <AppShell pageTitle="Contracts">
      <div className="contract-list">
        <div className="contract-list__header">
          <h1>Contracts</h1>
          <Button icon={Plus} onClick={() => navigate('/contracts/new')}>
            New Contract
          </Button>
        </div>

        <div className="contract-list__filters">
          <div className="filter-search">
            <Search size={15} strokeWidth={1.75} className="filter-search__icon" />
            <input
              className="filter-search__input"
              type="text"
              placeholder="Search by title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Select
            options={CONTRACT_TYPE_OPTIONS}
            placeholder="All types"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="filter-select"
          />
          <Select
            options={STATUS_OPTIONS}
            placeholder="All statuses"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          />
        </div>

        {loading ? (
          <LoadingState />
        ) : (
          <div className="contract-list__table">
            {filtered.length === 0 ? (
              <EmptyState
                icon={FileText}
                title="No contracts found"
                description={
                  search || typeFilter || statusFilter
                    ? 'Try adjusting your filters.'
                    : 'Create your first contract to get started.'
                }
                action={
                  !search && !typeFilter && !statusFilter ? (
                    <Button icon={Plus} onClick={() => navigate('/contracts/new')}>
                      New Contract
                    </Button>
                  ) : null
                }
              />
            ) : (
              <DataTable
                columns={columns}
                data={filtered}
                onRowClick={(row) => navigate(`/contracts/${row.id}`)}
              />
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
