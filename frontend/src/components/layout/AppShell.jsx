import Sidebar from './Sidebar.jsx';
import Topbar from './Topbar.jsx';
import './AppShell.css';

export default function AppShell({ children, pageTitle }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-shell__main">
        <Topbar pageTitle={pageTitle} />
        <main className="app-shell__content">
          {children}
        </main>
      </div>
    </div>
  );
}
