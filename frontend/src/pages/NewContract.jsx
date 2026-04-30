import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell.jsx';
import Input from '../components/common/Input.jsx';
import Select from '../components/common/Select.jsx';
import Textarea from '../components/common/Textarea.jsx';
import Button from '../components/common/Button.jsx';
import { useToast } from '../components/common/Toast.jsx';
import { createContract } from '../api/contracts.js';
import { CONTRACT_TYPE_OPTIONS, JURISDICTION_OPTIONS } from '../utils/labels.js';
import './NewContract.css';

export default function NewContract() {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [form, setForm] = useState({
    title: '',
    contractType: '',
    jurisdiction: '',
    description: '',
    tags: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const validate = () => {
    const errs = {};
    if (!form.title.trim()) errs.title = 'Title is required';
    if (!form.contractType) errs.contractType = 'Contract type is required';
    if (!form.jurisdiction) errs.jurisdiction = 'Jurisdiction is required';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }
    setLoading(true);
    try {
      const contract = await createContract({
        title: form.title.trim(),
        contractType: form.contractType,
        jurisdiction: form.jurisdiction,
        description: form.description.trim() || null,
        tags: form.tags.trim() || null,
      });
      showToast('Contract created', 'success');
      navigate(`/contracts/${contract.id}`);
    } catch (err) {
      showToast(err.message || 'Failed to create contract', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell pageTitle="New Contract">
      <div className="new-contract">
        <div className="new-contract__header">
          <h1>New Contract</h1>
          <p>Fill in the details to begin drafting a new contract.</p>
        </div>

        <form onSubmit={handleSubmit} className="new-contract__form">
          <div className="form-card">
            <h3 className="form-card__title">Contract Details</h3>

            <Input
              id="title"
              label="Title"
              value={form.title}
              onChange={set('title')}
              placeholder="e.g. Software License Agreement with Acme Corp"
              required
              error={errors.title}
              autoFocus
            />

            <div className="form-row">
              <Select
                id="contractType"
                label="Contract Type"
                value={form.contractType}
                onChange={set('contractType')}
                options={CONTRACT_TYPE_OPTIONS}
                placeholder="Select type"
                required
                error={errors.contractType}
              />
              <Select
                id="jurisdiction"
                label="Jurisdiction"
                value={form.jurisdiction}
                onChange={set('jurisdiction')}
                options={JURISDICTION_OPTIONS}
                placeholder="Select jurisdiction"
                required
                error={errors.jurisdiction}
              />
            </div>

            <Textarea
              id="description"
              label="Description"
              value={form.description}
              onChange={set('description')}
              placeholder="Brief description of this contract (optional)"
              rows={3}
            />

            <Input
              id="tags"
              label="Tags"
              value={form.tags}
              onChange={set('tags')}
              placeholder="e.g. confidential, vendor, 2025"
              hint="Comma-separated tags for organization"
            />
          </div>

          <div className="new-contract__actions">
            <Button
              type="button"
              variant="ghost"
              onClick={() => navigate('/contracts')}
            >
              Cancel
            </Button>
            <Button type="submit" loading={loading}>
              Create Contract
            </Button>
          </div>
        </form>
      </div>
    </AppShell>
  );
}
