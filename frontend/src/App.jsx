import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import SearchTab from './components/SearchTab';
import ChatTab from './components/ChatTab';
import DashboardTab from './components/DashboardTab';
import UploadTab from './components/UploadTab';
import CrawlerTab from './components/CrawlerTab';
import './App.css';

const PAGE_LABELS = {
  search: 'Semantic Search',
  chat: 'AI Assistant',
  upload: 'Data Ingestion',
  dashboard: 'Analytics',
  crawler: 'Web Crawler',
};

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [transitioning, setTransitioning] = useState(false);

  const switchTab = (tab) => {
    if (tab === activeTab) return;
    setTransitioning(true);
    setTimeout(() => {
      setActiveTab(tab);
      setTransitioning(false);
    }, 160);
  };

  const isChat = activeTab === 'chat';

  const CONTENT = {
    search: <SearchTab />,
    chat: <ChatTab />,
    upload: <UploadTab />,
    dashboard: <DashboardTab />,
    crawler: <CrawlerTab />,
  };

  return (
    <div className="app-shell">
      {/* Ambient Blobs */}
      <div className="ambient-bg">
        <div className="ambient-blob ambient-blob-1" />
        <div className="ambient-blob ambient-blob-2" />
        <div className="ambient-blob ambient-blob-3" />
      </div>

      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={switchTab} />

      {/* Main */}
      <div className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <div className="topbar-breadcrumb">
            <span style={{ color: 'var(--text-muted)' }}>UniSearch</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
            <span>{PAGE_LABELS[activeTab]}</span>
          </div>
          <div className="topbar-actions">
            <span className="topbar-badge">v4.0 GENESIS</span>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-container">
          <div
            style={{
              position: 'absolute', inset: 0,
              opacity: transitioning ? 0 : 1,
              transform: transitioning ? 'translateY(6px)' : 'translateY(0)',
              transition: 'opacity 0.16s ease, transform 0.16s ease',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            {isChat ? (
              <div style={{ flex: 1, overflow: 'hidden' }}>
                {CONTENT.chat}
              </div>
            ) : (
              <div style={{ flex: 1, overflowY: 'auto', padding: '32px 36px' }}>
                {CONTENT[activeTab]}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
