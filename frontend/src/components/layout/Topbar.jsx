import { useAuth } from '../../context/AuthContext.jsx';
import './Topbar.css';

export default function Topbar({ pageTitle }) {
  const { user } = useAuth();

  return (
    <header className="topbar">
      <h3 className="topbar__title">{pageTitle}</h3>
      {user && (
        <span className="topbar__user">
          {user.full_name || user.email}
        </span>
      )}
    </header>
  );
}
