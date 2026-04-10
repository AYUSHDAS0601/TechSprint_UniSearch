import React, { useState, useEffect, useCallback } from 'react';
import { fetchStats, fetchLogs } from '../api';

const RefreshIcon = ({ spinning }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    style={{ animation: spinning ? 'spin 0.8s linear infinite' : 'none' }}>
    <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
  </svg>
);

const STAT_CARDS = [
  {
    key: 'total_vectors',
    label: 'Vector Embeddings',
    icon: '🧮',
    desc: 'Indexed chunks',
    color: '#06b6d4',
  },
  {
    key: 'total_documents',
    label: 'Raw Documents',
    icon: '📄',
    desc: 'Files in archive',
    color: '#818cf8',
  },
  {
    key: 'status',
    label: 'System Status',
    icon: '⚡',
    desc: 'All systems go',
    color: '#10b981',
  },
  {
    key: 'llm_model',
    label: 'Active LLM',
    icon: '🤖',
    desc: 'Ollama engine',
    color: '#f59e0b',
  },
];

const DashboardTab = () => {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [s, l] = await Promise.all([fetchStats(), fetchLogs(40)]);
      setStats(s);
      setLogs(l.logs || []);
    } catch {
      /* silently fail */
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const t = setInterval(loadData, 15000);
    return () => clearInterval(t);
  }, [loadData]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const getValue = (key) => {
    if (!stats) return '—';
    const v = stats[key];
    if (v === undefined || v === null) return '—';
    return String(v);
  };

  return (
    <div className="page-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h2>System Analytics</h2>
          <p>Real-time metrics and operational logs from the vector index and processing pipeline.</p>
        </div>
        <button
          id="refresh-dashboard"
          onClick={handleRefresh}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '8px 16px', borderRadius: '8px',
            background: 'var(--bg-elevated)', border: '1px solid var(--border-default)',
            color: 'var(--text-secondary)', fontSize: '12px', fontWeight: 600,
            cursor: 'pointer', transition: 'all 0.2s ease', fontFamily: 'inherit',
          }}
        >
          <RefreshIcon spinning={refreshing} /> Refresh
        </button>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {STAT_CARDS.map((card, i) => (
          <div
            key={card.key}
            className={`stat-card animate-in stagger-${i + 1}`}
          >
            <div className="stat-card-accent" style={{ background: `linear-gradient(90deg, ${card.color}, transparent)` }} />
            <div className="stat-card-icon" style={{ background: `${card.color}18`, color: card.color }}>
              {card.icon}
            </div>
            {loading ? (
              <div style={{ height: '42px', background: 'var(--bg-elevated)', borderRadius: '8px', marginBottom: '6px', animation: 'textPulse 1.5s ease infinite' }} />
            ) : (
              <div className="stat-card-value">{getValue(card.key)}</div>
            )}
            <div className="stat-card-label">{card.label}</div>
          </div>
        ))}
      </div>

      {/* Log panel */}
      <div className="log-panel animate-in stagger-4">
        <div className="log-panel-header">
          <div className="log-panel-title">
            <span>⬤</span> System Logs
          </div>
          <div className="live-badge">
            <div className="status-dot" />
            LIVE
          </div>
        </div>
        <div className="log-content">
          {loading ? (
            <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Loading logs...</div>
          ) : logs.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No log entries found. Run an operation to see activity here.</div>
          ) : (
            logs.map((line, i) => (
              <div key={i} className="log-line">
                <span className="log-number">{String(i + 1).padStart(3, '0')}</span>
                <span className="log-text">{line.trim()}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardTab;
