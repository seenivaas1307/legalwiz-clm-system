import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FileText, Users, ListOrdered, FormInput,
  Eye, ArrowLeft, MessageSquare, History,
} from 'lucide-react';
import AppShell from '../components/layout/AppShell.jsx';
import ContractStepper from '../components/stepper/ContractStepper.jsx';
import StatusBadge from '../components/common/StatusBadge.jsx';
import LoadingState from '../components/common/LoadingState.jsx';
import { useToast } from '../components/common/Toast.jsx';
import { getContract } from '../api/contracts.js';
import { CONTRACT_TYPE_LABELS } from '../utils/labels.js';
import { formatDate } from '../utils/date.js';

// Step components
import SetupStep     from './contract-steps/SetupStep.jsx';
import PartiesStep   from './contract-steps/PartiesStep.jsx';
import ClausesStep   from './contract-steps/ClausesStep.jsx';
import FillDetailsStep from './contract-steps/FillDetailsStep.jsx';
import ReviewStep    from './contract-steps/ReviewStep.jsx';

// Floating auxiliary
import ChatDrawer      from '../components/chat/ChatDrawer.jsx';
import HistoryDropdown from '../components/history/HistoryDropdown.jsx';

import './ContractDetail.css';

// ── Step definitions ───────────────────────────────────────────────────────
const STEPS = [
  { key: 'setup',   label: 'Setup',        icon: FileText     },
  { key: 'parties', label: 'Parties',       icon: Users        },
  { key: 'clauses', label: 'Clauses',       icon: ListOrdered  },
  { key: 'fill',    label: 'Fill Details',  icon: FormInput    },
  { key: 'review',  label: 'Review',        icon: Eye          },
];

// Step order for Prev/Next navigation
const STEP_KEYS = STEPS.map((s) => s.key);

export default function ContractDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [contract, setContract]       = useState(null);
  const [loading, setLoading]         = useState(true);
  const [activeStep, setActiveStep]   = useState('setup');
  const [doneSteps, setDoneSteps]     = useState(new Set());

  // Auxiliary panel states
  const [chatOpen, setChatOpen]       = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);

  const loadContract = useCallback(() => {
    setLoading(true);
    getContract(id)
      .then(setContract)
      .catch((err) => {
        showToast(err.message || 'Failed to load contract', 'error');
        navigate('/contracts');
      })
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { loadContract(); }, [loadContract]);

  if (loading) return <AppShell pageTitle="Loading…"><LoadingState /></AppShell>;
  if (!contract) return null;

  // ── Step navigation helpers ──────────────────────────────────────────────
  const goToStep = (key) => setActiveStep(key);

  const markDone = (key) => setDoneSteps((prev) => new Set(prev).add(key));

  const handleNext = () => {
    const idx = STEP_KEYS.indexOf(activeStep);
    if (idx < STEP_KEYS.length - 1) {
      markDone(activeStep);
      setActiveStep(STEP_KEYS[idx + 1]);
    }
  };

  const handlePrev = () => {
    const idx = STEP_KEYS.indexOf(activeStep);
    if (idx > 0) setActiveStep(STEP_KEYS[idx - 1]);
  };

  // Shared props passed to every step
  const stepProps = {
    contractId: id,
    contract,
    onContractUpdate: loadContract,
    onNext: handleNext,
    onPrev: handlePrev,
    markDone,
  };

  return (
    <AppShell pageTitle={contract.title}>
      <div className="contract-detail fade-in">

        {/* ── Top bar: back + auxiliary controls ──────────────────────── */}
        <div className="contract-detail__topbar">
          <button
            className="contract-detail__back"
            onClick={() => navigate('/contracts')}
          >
            <ArrowLeft size={15} strokeWidth={1.75} />
            Contracts
          </button>

          <div className="contract-detail__aux-actions">
            <button
              className="contract-detail__aux-btn"
              onClick={() => setHistoryOpen((v) => !v)}
              title="Version history"
            >
              <History size={16} strokeWidth={1.75} />
            </button>
            <button
              className="contract-detail__aux-btn"
              onClick={() => setChatOpen((v) => !v)}
              title="AI assistant"
            >
              <MessageSquare size={16} strokeWidth={1.75} />
            </button>
          </div>
        </div>

        {/* ── Contract header ─────────────────────────────────────────── */}
        <div className="contract-detail__header">
          <div className="contract-detail__title-row">
            <h1>{contract.title}</h1>
          </div>
          <div className="contract-detail__meta">
            <StatusBadge status={contract.status} />
            <span className="contract-detail__type text-mono">
              {CONTRACT_TYPE_LABELS[contract.contract_type] || contract.contract_type}
            </span>
            <span className="contract-detail__jurisdiction">{contract.jurisdiction}</span>
            <span className="contract-detail__date">Created {formatDate(contract.created_at)}</span>
          </div>
        </div>

        {/* ── 5-step stepper ──────────────────────────────────────────── */}
        <ContractStepper
          steps={STEPS}
          activeStep={activeStep}
          doneSteps={doneSteps}
          onStepClick={goToStep}
          showNav={false}   /* Each step renders its own nav bar */
        >
          {activeStep === 'setup'   && <SetupStep   {...stepProps} />}
          {activeStep === 'parties' && <PartiesStep {...stepProps} />}
          {activeStep === 'clauses' && <ClausesStep {...stepProps} />}
          {activeStep === 'fill'    && <FillDetailsStep {...stepProps} />}
          {activeStep === 'review'  && <ReviewStep  {...stepProps} />}
        </ContractStepper>

      </div>

      {/* ── Floating auxiliary panels ────────────────────────────────── */}
      <ChatDrawer
        contractId={id}
        contract={contract}
        open={chatOpen}
        onClose={() => setChatOpen(false)}
      />
      <HistoryDropdown
        contractId={id}
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onContractUpdate={loadContract}
      />
    </AppShell>
  );
}
