import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// ─── Search ───────────────────────────────────────────────────────────────────
export const searchDocuments = async (query, categories = [], k = 8) => {
  const res = await api.post('/api/search', { query, categories, k });
  return res.data;
};

// ─── Q&A ──────────────────────────────────────────────────────────────────────
export const askQA = async (question, k = 5) => {
  const res = await api.post('/api/qa', { question, k });
  return res.data;
};

// ─── Stats ────────────────────────────────────────────────────────────────────
export const fetchStats = async () => {
  const res = await api.get('/api/stats');
  return res.data;
};

// ─── Logs ────────────────────────────────────────────────────────────────────
export const fetchLogs = async (lines = 30) => {
  const res = await api.get(`/api/logs?lines=${lines}`);
  return res.data;
};

// ─── File upload / ingest ─────────────────────────────────────────────────────
export const uploadFiles = async (files) => {
  const form = new FormData();
  files.forEach(f => form.append('files', f));
  const res = await api.post('/api/ingest', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  });
  return res.data;
};

// ─── Dynamic web crawler ──────────────────────────────────────────────────────
export const startCrawl = async ({ urls, maxPages = 25, maxDepth = 2, sameDomainOnly = true }) => {
  const res = await api.post('/api/crawl/start', {
    urls,
    max_pages: maxPages,
    max_depth: maxDepth,
    same_domain_only: sameDomainOnly,
    index_immediately: true,
  });
  return res.data;
};

export const getCrawlStatus = async () => {
  const res = await api.get('/api/crawl/status');
  return res.data;
};

export const stopCrawl = async () => {
  const res = await api.post('/api/crawl/stop');
  return res.data;
};

export const triggerScrape = async () => {
  const res = await api.post('/api/scrape');
  return res.data;
};

// ─── Health ───────────────────────────────────────────────────────────────────
export const checkHealth = async () => {
  const res = await api.get('/api/health');
  return res.data;
};

export default api;
