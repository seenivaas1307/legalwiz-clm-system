import { useState, useEffect } from 'react';
import { BookTemplate, Plus, Trash2 } from 'lucide-react';
import AppShell from '../components/layout/AppShell.jsx';
import Button from '../components/common/Button.jsx';
import Modal from '../components/common/Modal.jsx';
import Input from '../components/common/Input.jsx';
import Textarea from '../components/common/Textarea.jsx';
import LoadingState from '../components/common/LoadingState.jsx';
import EmptyState from '../components/common/EmptyState.jsx';
import DataTable from '../components/common/DataTable.jsx';
import { useToast } from '../components/common/Toast.jsx';
import { listTemplates, deleteTemplate } from '../api/templates.js';
import { CONTRACT_TYPE_LABELS } from '../utils/labels.js';
import { formatDate } from '../utils/date.js';
import './Templates.css';

export default function Templates() {
  const { showToast } = useToast();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = () => {
    setLoading(true);
    listTemplates()
      .then((d) => setTemplates(Array.isArray(d) ? d : d?.templates || []))
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async () => {
    try {
      await deleteTemplate(deleteTarget.id);
      showToast('Template deleted', 'success');
      setDeleteTarget(null);
      load();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const columns = [
    {
      key: 'name',
      label: 'Name',
      render: (v) => <span className="table-title">{v}</span>,
    },
    {
      key: 'contract_type',
      label: 'Type',
      render: (v) => <span className="text-mono" style={{ color: 'var(--ink-tertiary)' }}>{CONTRACT_TYPE_LABELS[v] || v}</span>,
    },
    {
      key: 'jurisdiction',
      label: 'Jurisdiction',
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (v) => <span style={{ color: 'var(--ink-tertiary)', fontSize: '0.8125rem' }}>{formatDate(v)}</span>,
    },
    {
      key: 'id',
      label: '',
      width: '60px',
      render: (v, row) => (
        <Button variant="ghost" size="sm" icon={Trash2} onClick={(e) => { e.stopPropagation(); setDeleteTarget(row); }} />
      ),
    },
  ];

  return (
    <AppShell pageTitle="Templates">
      <div className="templates-page">
        <div className="templates-header">
          <h1>Templates</h1>
          <p>Reusable contract configurations. Save any contract as a template to quickly replicate its clause setup.</p>
        </div>

        {loading ? <LoadingState /> : (
          <div className="templates-table">
            {templates.length === 0 ? (
              <EmptyState
                icon={BookTemplate}
                title="No templates yet"
                description="Open any contract and save it as a template from the Overview tab."
              />
            ) : (
              <DataTable columns={columns} data={templates} />
            )}
          </div>
        )}

        <Modal
          isOpen={!!deleteTarget}
          onClose={() => setDeleteTarget(null)}
          title="Delete Template"
          footer={
            <>
              <Button variant="ghost" onClick={() => setDeleteTarget(null)}>Cancel</Button>
              <Button variant="danger" onClick={handleDelete}>Delete</Button>
            </>
          }
        >
          <p>Delete <strong>{deleteTarget?.name}</strong>? This cannot be undone.</p>
        </Modal>
      </div>
    </AppShell>
  );
}
