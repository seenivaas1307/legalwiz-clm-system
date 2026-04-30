/**
 * HistoryDropdown — Floating version history panel
 * Stub — wraps existing HistoryTab in a popover panel.
 * Full styled implementation in Session 8.
 */
import { X } from 'lucide-react';
import HistoryTab from '../../pages/contract-tabs/HistoryTab.jsx';
import './HistoryDropdown.css';

export default function HistoryDropdown({ contractId, open, onClose, onContractUpdate }) {
  if (!open) return null;

  return (
    <>
      <div className="history-dropdown__backdrop" onClick={onClose} />
      <div className="history-dropdown" role="dialog" aria-label="Version history">
        <div className="history-dropdown__header">
          <span className="history-dropdown__title">Version History</span>
          <button className="history-dropdown__close" onClick={onClose} aria-label="Close">
            <X size={16} strokeWidth={2} />
          </button>
        </div>
        <div className="history-dropdown__body">
          <HistoryTab contractId={contractId} onContractUpdate={onContractUpdate || (() => {})} />
        </div>
      </div>
    </>
  );
}
