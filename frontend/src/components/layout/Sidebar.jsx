import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  BookTemplate,
  LogOut,
  Plus,
  Building2,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext.jsx';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/contracts', icon: FileText,        label: 'Contracts' },
  { to: '/templates', icon: BookTemplate,    label: 'Templates' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__logo">LegalWiz</span>
      </div>

      {/* ── New Contract CTA ── */}
      <div className="sidebar__cta-wrap">
        <button
          className="sidebar__cta"
          onClick={() => navigate('/contracts/new')}
          type="button"
        >
          <Plus size={15} strokeWidth={2.5} />
          New Contract
        </button>
      </div>

      <nav className="sidebar__nav" aria-label="Main navigation">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `sidebar__item ${isActive ? 'sidebar__item--active' : ''}`
            }
            end={to === '/dashboard'}
          >
            <Icon size={17} strokeWidth={1.75} className="sidebar__icon" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        {user && (
          <span className="sidebar__user" title={user.email}>
            {user.email}
          </span>
        )}
        <button className="sidebar__logout" onClick={handleLogout}>
          <LogOut size={15} strokeWidth={1.75} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
