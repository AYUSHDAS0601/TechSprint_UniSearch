import React, { useState, useRef, useCallback } from 'react';
import { uploadFiles, triggerScrape } from '../api';

const UploadIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const FileIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

const XIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

const SpiderIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M12 2v4M12 18v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M2 12h4M18 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
  </svg>
);

const LoaderIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    style={{ animation: 'spin 0.8s linear infinite' }}>
    <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
    <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
  </svg>
);

const ACCEPT = 'application/pdf,image/png,image/jpeg,image/jpg';

const UploadTab = () => {
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [toast, setToast] = useState(null); // { type: 'success'|'error'|'loading', msg }
  const fileInputRef = useRef();

  const addFiles = (incoming) => {
    const filtered = Array.from(incoming).filter(f =>
      ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'].includes(f.type)
    );
    setFiles(prev => {
      const names = new Set(prev.map(p => p.name));
      return [...prev, ...filtered.filter(f => !names.has(f.name))];
    });
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    addFiles(e.dataTransfer.files);
  }, []);

  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = () => setDragOver(false);

  const removeFile = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i));

  const showToast = (type, msg, autoClear = 5000) => {
    setToast({ type, msg });
    if (autoClear) setTimeout(() => setToast(null), autoClear);
  };

  const handleUpload = async () => {
    if (!files.length) return;
    showToast('loading', `Ingesting ${files.length} document(s)…`, 0);
    try {
      const data = await uploadFiles(files);
      setFiles([]);
      showToast('success', `✓ Successfully indexed ${data.processed_files?.length || files.length} files.`);
    } catch {
      showToast('error', '✕ Upload failed. Check that the backend is running.');
    }
  };

  const handleSpider = async () => {
    showToast('loading', 'Spider crawling university site for notices…', 0);
    try {
      const data = await triggerScrape();
      showToast('success', `✓ Spider acquired ${data.count} new documents.`);
    } catch {
      showToast('error', '✕ Spider failed. Check backend logs for details.');
    }
  };

  return (
    <div className="page-view">
      <div className="page-header">
        <h2>Data Ingestion Portal</h2>
        <p>Upload PDF or image documents directly, or run the automated web spider to fetch notices from the university site.</p>
      </div>

      <div className="ingest-grid">
        {/* Drop Zone */}
        <div
          id="drop-zone"
          className={`upload-zone${dragOver ? ' drag-over' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-zone-icon"><UploadIcon /></div>
          <h3>Upload Documents</h3>
          <p>Drag & drop PDFs or images here, or click to browse your files.</p>
          <button
            type="button"
            className="primary-btn"
            style={{ width: 'auto', padding: '10px 24px' }}
            onClick={e => { e.stopPropagation(); fileInputRef.current?.click(); }}
          >
            Browse Files
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ACCEPT}
            style={{ display: 'none' }}
            onChange={e => addFiles(e.target.files)}
          />
          <p style={{ marginTop: '14px', fontSize: '11px', color: 'var(--text-muted)', margin: '14px 0 0' }}>
            Accepts: PDF, PNG, JPG
          </p>
        </div>

        {/* Spider card */}
        <div className="spider-card">
          <div className="spider-card-icon"><SpiderIcon /></div>
          <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
            Web Spider
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '22px', maxWidth: '240px' }}>
            Automatically crawl the configured university URLs and download new notices.
          </p>
          <button id="run-spider-btn" className="spider-btn" onClick={handleSpider}>
            Launch Spider
          </button>
        </div>
      </div>

      {/* File Queue */}
      {files.length > 0 && (
        <div className="file-queue">
          <div className="file-queue-header">
            Pending ingestion — {files.length} file{files.length > 1 ? 's' : ''}
          </div>
          {files.map((f, i) => (
            <div key={i} className="file-row">
              <FileIcon />
              <span className="file-name">{f.name}</span>
              <span className="file-size">{(f.size / 1024).toFixed(1)} KB</span>
              <button className="file-remove" onClick={() => removeFile(i)} aria-label="Remove file">
                <XIcon />
              </button>
            </div>
          ))}
          <div style={{ padding: '16px 20px' }}>
            <button
              id="ingest-upload-btn"
              className="primary-btn"
              onClick={handleUpload}
              disabled={toast?.type === 'loading'}
            >
              {toast?.type === 'loading' ? (
                <><LoaderIcon /> Processing...</>
              ) : (
                'Index Documents'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className={`toast-banner ${toast.type}`}>
          {toast.type === 'loading' && <LoaderIcon />}
          {toast.msg}
        </div>
      )}
    </div>
  );
};

export default UploadTab;
