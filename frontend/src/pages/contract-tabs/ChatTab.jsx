import { useState, useEffect, useCallback, useRef } from 'react';
import { Send, Trash2 } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { sendMessage, getChatHistory, clearChatHistory } from '../../api/chatbot.js';
import { formatDateTime } from '../../utils/date.js';
import './ChatTab.css';

function ChatMessage({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`chat-msg chat-msg--${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-msg__bubble">
        <div className="chat-msg__text">{msg.content || msg.message}</div>
        {msg.citations && msg.citations.length > 0 && (
          <div className="chat-msg__citations">
            {msg.citations.map((c, i) => (
              <span key={i} className="chat-citation">
                {c.clause_type || c.source}
              </span>
            ))}
          </div>
        )}
        <div className="chat-msg__time">{formatDateTime(msg.created_at || msg.timestamp)}</div>
      </div>
    </div>
  );
}

export default function ChatTab({ contractId }) {
  const { showToast } = useToast();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  const loadHistory = useCallback(() => {
    setLoading(true);
    getChatHistory(contractId)
      .then((h) => setMessages(Array.isArray(h) ? h : h?.messages || []))
      .catch(() => setMessages([]))
      .finally(() => setLoading(false));
  }, [contractId]);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;
    const msg = input.trim();
    setInput('');
    setSending(true);

    // Optimistic user message
    const optimistic = { role: 'user', content: msg, created_at: new Date().toISOString() };
    setMessages((prev) => [...prev, optimistic]);

    try {
      const result = await sendMessage(contractId, msg);
      const assistantMsg = {
        role: 'assistant',
        content: result.answer || result.response || result.message || '',
        citations: result.citations || [],
        created_at: result.created_at || result.timestamp || new Date().toISOString(),
      };
      setSending(false);
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setSending(false);
      showToast(err.message, 'error');
      setMessages((prev) => prev.slice(0, -1)); // Remove optimistic
    }
  };

  const handleClear = async () => {
    try {
      await clearChatHistory(contractId);
      setMessages([]);
      showToast('Chat cleared', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  return (
    <div className="chat-tab">
      <div className="chat-header">
        <div>
          <h3>Contract Chat</h3>
          <p>Ask questions about this contract. The AI uses your clauses as source material.</p>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" icon={Trash2} onClick={handleClear}>
            Clear
          </Button>
        )}
      </div>

      <div className="chat-messages">
        {loading ? (
          <LoadingState message="Loading chat history..." />
        ) : messages.length === 0 && !sending ? (
          <div className="chat-empty">
            <p>No messages yet.</p>
            <p>Try: "What are the key obligations of Party A?" or "Summarize the termination clause."</p>
          </div>
        ) : (
          messages.map((msg, idx) => <ChatMessage key={idx} msg={msg} />)
        )}
        {sending && (
          <div className="chat-msg chat-msg--assistant">
            <div className="chat-msg__bubble">
              <div className="chat-thinking">
                <span className="chat-thinking__dot" />
                <span className="chat-thinking__dot" />
                <span className="chat-thinking__dot" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="chat-input-row">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something about this contract..."
          disabled={sending}
        />
        <button type="submit" className="chat-send-btn" disabled={!input.trim() || sending}>
          <Send size={16} strokeWidth={1.75} />
        </button>
      </form>
    </div>
  );
}
