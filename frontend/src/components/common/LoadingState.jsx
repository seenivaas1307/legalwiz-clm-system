import { Loader2 } from 'lucide-react';
import './LoadingState.css';

export default function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="loading-state">
      <Loader2 size={20} strokeWidth={1.5} className="loading-state__icon spin" />
      <span className="loading-state__text">{message}</span>
    </div>
  );
}
