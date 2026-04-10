import React from 'react';

const MENU_ITEMS = [
  {
    id: 'search',
    label: 'Semantic Search',
    path: 'M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z',
    badge: null,
  },
  {
    id: 'chat',
    label: 'AI Assistant',
    path: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z',
    badge: null,
  },
  {
    id: 'crawler',
    label: 'Web Crawler',
    path: 'M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zM2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20',
    badge: 'DYNAMIC',
  },
  {
    id: 'upload',
    label: 'Data Ingestion',
    path: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12',
    badge: null,
  },
  {
    id: 'dashboard',
    label: 'Analytics',
    path: 'M18 20V10M12 20V4M6 20v-6',
    badge: null,
  },
];

const NavIcon = ({ path }) => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
);

const Sidebar = ({ activeTab, setActiveTab }) => (
  <aside className="sidebar">
    <div className="sidebar-logo">
      <div className="sidebar-logo-inner">
        <div className="sidebar-logo-icon">🏛</div>
        <div className="sidebar-logo-text">
          <h1>UniSearch</h1>
          <p>Digital Archaeology</p>
        </div>
      </div>
    </div>

    <nav className="sidebar-nav">
      <div className="nav-section-label">Navigation</div>
      {MENU_ITEMS.map(item => (
        <button
          key={item.id}
          className={`nav-item${activeTab === item.id ? ' active' : ''}`}
          onClick={() => setActiveTab(item.id)}
          aria-label={item.label}
          id={`nav-${item.id}`}
        >
          <NavIcon path={item.path} />
          <span className="nav-item-label">{item.label}</span>
          {item.badge && <span className="nav-badge">{item.badge}</span>}
        </button>
      ))}
    </nav>

    <div className="sidebar-footer">
      <div className="status-pill">
        <div className="status-dot" />
        All systems nominal
      </div>
    </div>
  </aside>
);

export default Sidebar;
