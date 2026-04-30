/**
 * ChatDrawer — Floating AI chat panel
 * Stub — wraps existing ChatTab in a slide-over drawer.
 * Full styled implementation in Session 8.
 */
import { X } from 'lucide-react';
import ChatTab from '../../pages/contract-tabs/ChatTab.jsx';
import './ChatDrawer.css';

export default function ChatDrawer({ contractId, contract, open, onClose }) {
  if (!open) return null;

  return (
    <>
      <div className="chat-drawer__backdrop" onClick={onClose} />
      <div className="chat-drawer" role="dialog" aria-label="AI Assistant">
        <div className="chat-drawer__header">
          <span className="chat-drawer__title">AI Assistant</span>
          <button className="chat-drawer__close" onClick={onClose} aria-label="Close">
            <X size={16} strokeWidth={2} />
          </button>
        </div>
        <div className="chat-drawer__body">
          <ChatTab contractId={contractId} contract={contract} />
        </div>
      </div>
    </>
  );
}
