import React, { useState } from 'react';
import { searchDocuments } from '../api';

const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
  </svg>
);

const FileIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

const CalIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
);

const CATEGORY_OPTIONS = ['Examination', 'Scholarship', 'Events', 'General', 'Administrative', 'Academic'];

const SearchTab = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [categories, setCategories] = useState([]);

  const toggleCategory = (cat) => {
    setCategories(prev =>
      prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
    );
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    const t0 = performance.now();
    try {
      const data = await searchDocuments(query, categories);
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setElapsed(((performance.now() - t0) / 1000).toFixed(3));
      setLoading(false);
    }
  };

  const handleKey = (e) => { if (e.key === 'Enter') handleSearch(); };

  return (
    <div className="page-view">
      <div className="page-header">
        <h2>Semantic Document Search</h2>
        <p>Find university notices, schedules and circulars using natural language — powered by FAISS vector search.</p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch}>
        <div className="search-bar-wrap">
          <SearchIcon />
          <input
            id="search-query"
            type="text"
            className="search-input"
            placeholder="e.g. 'B.Tech CSE exam schedule' or 'scholarship deadline'"
            value={query}
            onChange={e => setQuery(e.target.value)}
            autoFocus
          />
          <button type="submit" className="search-btn">Search</button>
        </div>
      </form>

      {/* Filters */}
      <div className="filter-row">
        <span className="filter-label">Filter:</span>
        {CATEGORY_OPTIONS.map(cat => (
          <button
            key={cat}
            id={`filter-${cat.toLowerCase()}`}
            className={`filter-chip${categories.includes(cat) ? ' active' : ''}`}
            onClick={() => toggleCategory(cat)}
            type="button"
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="spinner-wrap">
          <div className="spinner" />
          <span className="spinner-text">Scaning vector space...</span>
        </div>
      )}

      {/* Results */}
      {!loading && searched && (
        <div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '18px', fontWeight: 600 }}>
            Found <span style={{ color: 'var(--accent-primary)' }}>{results.length}</span> results in {elapsed}s
          </p>

          {results.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><SearchIcon /></div>
              <h3>No documents found</h3>
              <p>Try different keywords or clear category filters to broaden your search.</p>
            </div>
          ) : (
            <div className="results-list">
              {results.map((res, i) => {
                const relevance = Math.max(0, (1 - (res.score || 0)) * 100);
                const excerpt = res.summary || res.content_snippet || 'No preview available.';
                const date = res.ingest_date ? new Date(res.ingest_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';

                return (
                  <div
                    key={i}
                    className="result-card animate-in"
                    style={{ animationDelay: `${i * 0.06}s`, opacity: 0 }}
                  >
                    <div className="result-card-header">
                      <div className="result-card-title-row">
                        <div className="result-card-icon"><FileIcon /></div>
                        <div>
                          <div className="result-card-title">{res.filename || 'Unknown Document'}</div>
                          <div className="result-card-meta">
                            <span className="result-card-meta-item">
                              <CalIcon /> {date}
                            </span>
                            <span className="result-card-meta-item" style={{ textTransform: 'capitalize' }}>
                              {res.type || '—'}
                            </span>
                            {res.file_size > 0 && (
                              <span className="result-card-meta-item font-mono" style={{ fontSize: '10px' }}>
                                {Math.round(res.file_size / 1024)} KB
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="result-score">
                        <div className="result-score-num">{relevance.toFixed(1)}%</div>
                        <div className="result-score-label">Match</div>
                      </div>
                    </div>

                    <p className="result-card-excerpt">"{excerpt.slice(0, 220)}{excerpt.length > 220 ? '…' : ''}"</p>

                    <div className="result-card-footer">
                      <div className="tag-list">
                        {(res.categories || ['General']).map(c => (
                          <span key={c} className="tag">{c}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Initial empty state */}
      {!loading && !searched && (
        <div className="empty-state">
          <div className="empty-state-icon" style={{ fontSize: '28px' }}>🔍</div>
          <h3>Start Searching</h3>
          <p>Enter a natural language query above to retrieve semantically matched documents from the archive.</p>
        </div>
      )}
    </div>
  );
};

export default SearchTab;
