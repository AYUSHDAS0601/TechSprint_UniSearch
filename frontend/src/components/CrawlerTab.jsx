import React, { useState, useEffect, useRef } from 'react';
import { startCrawl, getCrawlStatus, stopCrawl } from '../api';

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
    strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);

const TrashIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
);

const StopIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
    strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="3"/>
  </svg>
);

const PRESET_URLS = [
  { label: 'GIET University', url: 'https://www.giet.edu/' },
  { label: 'IIT Delhi', url: 'https://home.iitd.ac.in/' },
  { label: 'NIT Rourkela', url: 'https://nitrkl.ac.in/' },
  { label: 'VIT Vellore', url: 'https://vit.ac.in/' },
];

const CrawlerTab = () => {
  const [urls, setUrls] = useState(['']);
  const [maxPages, setMaxPages] = useState(20);
  const [maxDepth, setMaxDepth] = useState(2);
  const [sameDomain, setSameDomain] = useState(true);
  const [status, setStatus] = useState(null); // crawl status object
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState('');
  const logRef = useRef(null);
  const pollRef = useRef(null);

  // Poll crawl status
  useEffect(() => {
    if (polling) {
      pollRef.current = setInterval(async () => {
        try {
          const s = await getCrawlStatus();
          setStatus(s);
          if (!s.running) {
            setPolling(false);
            clearInterval(pollRef.current);
          }
        } catch { /* ignore */ }
      }, 1500);
    }
    return () => clearInterval(pollRef.current);
  }, [polling]);

  // Auto-scroll logs
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [status?.log]);

  const setUrl = (i, val) => {
    const next = [...urls];
    next[i] = val;
    setUrls(next);
  };

  const addUrl = () => setUrls([...urls, '']);
  const removeUrl = (i) => setUrls(urls.filter((_, idx) => idx !== i));

  const addPreset = (url) => {
    // If last entry is empty replace it, else append
    if (urls[urls.length - 1] === '') {
      setUrls([...urls.slice(0, -1), url]);
    } else if (!urls.includes(url)) {
      setUrls([...urls, url]);
    }
  };

  const handleStart = async () => {
    const cleaned = urls.map(u => u.trim()).filter(Boolean);
    if (!cleaned.length) {
      setError('Add at least one URL to crawl.');
      return;
    }
    setError('');
    try {
      await startCrawl({ urls: cleaned, maxPages, maxDepth, sameDomainOnly: sameDomain });
      setStatus({ running: true, pages_scraped: 0, files_downloaded: 0, indexed: 0, log: ['Starting...'], errors: [] });
      setPolling(true);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Failed to start crawl.');
    }
  };

  const handleStop = async () => {
    try { await stopCrawl(); } catch { /* ignore */ }
    setPolling(false);
    setStatus(s => s ? { ...s, running: false } : s);
  };

  const isRunning = status?.running;

  return (
    <div className="page-view" style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <h2>Dynamic Web Crawler</h2>
        <p>
          Paste any university website URL — the spider will crawl the pages, extract key information
          (titles, headings, dates, notices), and index everything into the search engine automatically.
        </p>
      </div>

      {/* Config panel */}
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)', padding: '28px', backdropFilter: 'blur(10px)',
      }}>
        {/* URL list */}
        <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', display: 'block', marginBottom: '12px' }}>
          Seed URLs
        </label>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px' }}>
          {urls.map((url, i) => (
            <div key={i} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                className="search-input"
                style={{
                  flex: 1, background: 'var(--bg-elevated)', border: '1px solid var(--border-default)',
                  borderRadius: '8px', padding: '10px 14px', fontSize: '14px',
                }}
                placeholder="https://university.edu/ or paste any page URL"
                value={url}
                onChange={e => setUrl(i, e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') addUrl(); }}
                disabled={isRunning}
              />
              {urls.length > 1 && (
                <button
                  onClick={() => removeUrl(i)}
                  disabled={isRunning}
                  style={{
                    background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
                    borderRadius: '8px', padding: '0 12px', cursor: 'pointer', color: '#ef4444',
                    transition: 'all 0.2s',
                  }}
                >
                  <TrashIcon />
                </button>
              )}
            </div>
          ))}
        </div>

        <button
          onClick={addUrl}
          disabled={isRunning}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '7px 14px', background: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)', borderRadius: '8px',
            color: 'var(--text-secondary)', fontSize: '12px', fontWeight: 600,
            cursor: 'pointer', fontFamily: 'inherit', marginBottom: '20px',
          }}
        >
          <PlusIcon /> Add URL
        </button>

        {/* Preset quick-add */}
        <div style={{ marginBottom: '24px' }}>
          <p style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: '10px' }}>
            Quick presets
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {PRESET_URLS.map(p => (
              <button
                key={p.url}
                onClick={() => addPreset(p.url)}
                disabled={isRunning}
                className="filter-chip"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Config sliders */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', display: 'block', marginBottom: '8px' }}>
              Max Pages — <span style={{ color: 'var(--accent-primary)' }}>{maxPages}</span>
            </label>
            <input type="range" min="5" max="100" value={maxPages}
              onChange={e => setMaxPages(+e.target.value)} disabled={isRunning}
              style={{ width: '100%', accentColor: 'var(--accent-primary)' }} />
          </div>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', display: 'block', marginBottom: '8px' }}>
              Crawl Depth — <span style={{ color: 'var(--accent-primary)' }}>{maxDepth}</span>
            </label>
            <input type="range" min="1" max="5" value={maxDepth}
              onChange={e => setMaxDepth(+e.target.value)} disabled={isRunning}
              style={{ width: '100%', accentColor: 'var(--accent-primary)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={sameDomain}
                onChange={e => setSameDomain(e.target.checked)}
                disabled={isRunning}
                style={{ accentColor: 'var(--accent-primary)', width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
                Same domain only
              </span>
            </label>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '26px', marginTop: '4px' }}>
              Restrict crawl to the seed URL's domain
            </p>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: '16px', padding: '12px 16px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '8px', color: '#ef4444', fontSize: '13px' }}>
            {error}
          </div>
        )}

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
          <button
            id="start-crawl-btn"
            className="primary-btn"
            onClick={handleStart}
            disabled={isRunning}
            style={{ flex: 1, opacity: isRunning ? 0.5 : 1 }}
          >
            {isRunning ? '⚙ Crawling…' : '🕷 Start Crawl'}
          </button>
          {isRunning && (
            <button
              onClick={handleStop}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '12px 20px', background: 'rgba(239,68,68,0.1)',
                border: '1px solid rgba(239,68,68,0.3)', borderRadius: 'var(--radius-lg)',
                color: '#ef4444', fontWeight: 700, cursor: 'pointer', fontSize: '13px',
                fontFamily: 'inherit',
              }}
            >
              <StopIcon /> Stop
            </button>
          )}
        </div>
      </div>

      {/* Live status */}
      {status && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)', overflow: 'hidden', backdropFilter: 'blur(10px)',
        }}>
          {/* Stat row */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
            borderBottom: '1px solid var(--border-subtle)',
          }}>
            {[
              { label: 'Pages Crawled', val: status.pages_scraped, color: 'var(--accent-primary)' },
              { label: 'Files Downloaded', val: status.files_downloaded, color: 'var(--accent-secondary)' },
              { label: 'Chunks Indexed', val: status.indexed, color: 'var(--accent-green)' },
              { label: 'Status', val: status.running ? 'Running' : (status.finished_at ? 'Done' : 'Idle'), color: status.running ? 'var(--accent-amber)' : 'var(--accent-green)' },
            ].map(({ label, val, color }) => (
              <div key={label} style={{ padding: '20px 24px', borderRight: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif', color, marginBottom: '4px' }}>{val}</div>
                <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Progress bar */}
          {status.running && (
            <div style={{ height: '2px', background: 'var(--bg-elevated)', position: 'relative', overflow: 'hidden' }}>
              <div style={{
                position: 'absolute', top: 0, left: '-100%', width: '100%', height: '100%',
                background: `linear-gradient(90deg, transparent, var(--accent-primary), transparent)`,
                animation: 'shimmer 1.5s linear infinite',
              }} />
            </div>
          )}

          {/* Live log */}
          <div style={{ padding: '14px 20px', background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
              Live Log
            </span>
          </div>
          <div
            ref={logRef}
            style={{
              height: '220px', overflowY: 'auto', padding: '14px 20px',
              background: 'rgba(0,0,0,0.3)', fontFamily: '"JetBrains Mono", monospace', fontSize: '12px',
            }}
          >
            {(status.log || []).map((line, i) => (
              <div key={i} style={{ marginBottom: '4px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                {line}
              </div>
            ))}
            {status.errors?.length > 0 && status.errors.map((e, i) => (
              <div key={`err-${i}`} style={{ color: '#ef4444', marginBottom: '4px' }}>⚠ {e}</div>
            ))}
          </div>

          {status.finished_at && !status.running && (
            <div style={{
              padding: '14px 20px',
              background: 'rgba(16,185,129,0.05)',
              borderTop: '1px solid rgba(16,185,129,0.15)',
              color: 'var(--accent-green)', fontSize: '13px', fontWeight: 600,
            }}>
              ✓ Crawl complete — {status.indexed} chunks indexed and ready to search!
              {status.errors?.length > 0 && (
                <span style={{ color: 'var(--accent-amber)', marginLeft: '12px' }}>
                  ({status.errors.length} error{status.errors.length > 1 ? 's' : ''})
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Shimmer animation */}
      <style>{`
        @keyframes shimmer {
          0% { left: -100%; }
          100% { left: 100%; }
        }
      `}</style>
    </div>
  );
};

export default CrawlerTab;
