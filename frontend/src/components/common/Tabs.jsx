import './Tabs.css';

export default function Tabs({ tabs, activeTab, onTabChange }) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = tab.key === activeTab;
        return (
          <button
            key={tab.key}
            role="tab"
            aria-selected={isActive}
            className={`tabs__tab ${isActive ? 'tabs__tab--active' : ''}`}
            onClick={() => onTabChange(tab.key)}
          >
            {Icon && <Icon size={15} strokeWidth={1.75} />}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
