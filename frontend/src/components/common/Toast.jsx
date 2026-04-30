import { useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import './Toast.css';

let toastId = 0;

// Global toast queue
let setToastsExternal = null;

export function useToast() {
  const showToast = useCallback((message, type = 'info') => {
    if (setToastsExternal) {
      const id = ++toastId;
      setToastsExternal((prev) => [...prev, { id, message, type }]);
      setTimeout(() => {
        setToastsExternal((prev) => prev.filter((t) => t.id !== id));
      }, 4000);
    }
  }, []);
  return { showToast };
}

export function ToastContainer() {
  const [toasts, setToasts] = useState([]);
  setToastsExternal = setToasts;

  const dismiss = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const icons = {
    success: <CheckCircle size={16} strokeWidth={1.75} />,
    error: <AlertCircle size={16} strokeWidth={1.75} />,
    info: <Info size={16} strokeWidth={1.75} />,
  };

  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast--${t.type}`}>
          <span className="toast__icon">{icons[t.type]}</span>
          <span className="toast__message">{t.message}</span>
          <button className="toast__dismiss" onClick={() => dismiss(t.id)} aria-label="Dismiss">
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
