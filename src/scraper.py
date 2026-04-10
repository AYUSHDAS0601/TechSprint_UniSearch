"""
Dynamic web crawler for university pages.
Takes any URL, extracts text content, and indexes it into FAISS.
Also supports downloading PDFs/images for OCR processing.
"""
import requests
from bs4 import BeautifulSoup
import logging
import json
import re
import random
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
from collections import deque
from .utils import setup_logging

logger = setup_logging("Scraper")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

DOWNLOAD_EXTS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
SKIP_EXTS = {'.js', '.css', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.map'}

def _url_ext(url: str) -> str:
    path = urlparse(url).path.lower()
    return Path(path).suffix if '.' in path else ''


class WebCrawler:
    """
    Flexible web crawler that:
    1. Accepts any seed URL(s)
    2. Extracts clean text from HTML pages  
    3. Downloads binary files (PDF/images) for OCR
    4. Saves key-value page records for indexing
    5. Optionally restricts to same domain
    """

    def __init__(
        self,
        download_dir: Path,
        data_dir: Path,
        rate_limit: float = 1.5,
        timeout: int = 12,
        retry_count: int = 2,
        same_domain_only: bool = True,
    ):
        self.download_dir = Path(download_dir)
        self.data_dir = Path(data_dir)
        self.pages_dir = self.data_dir / "crawled_pages"
        self.history_file = self.download_dir / "download_history.txt"

        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)

        self.rate_limit = rate_limit
        self.timeout = timeout
        self.retry_count = retry_count
        self.same_domain_only = same_domain_only

        self.downloaded_urls = self._load_history()
        self.session = requests.Session()
        self._rotate_ua()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _rotate_ua(self):
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def _load_history(self) -> set:
        if self.history_file.exists():
            return set(self.history_file.read_text().splitlines())
        return set()

    def _save_to_history(self, url: str):
        with open(self.history_file, 'a') as f:
            f.write(url + '\n')
        self.downloaded_urls.add(url)

    def _url_slug(self, url: str) -> str:
        """Short safe filename from URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    # ── fetch ─────────────────────────────────────────────────────────────────

    def _fetch(self, url: str):
        """Fetch URL, return (response, soup) or (None, None)."""
        for attempt in range(self.retry_count):
            try:
                resp = self.session.get(url, timeout=self.timeout, verify=False, allow_redirects=True)
                resp.raise_for_status()
                ct = resp.headers.get('Content-Type', '')
                if 'text/html' in ct:
                    soup = BeautifulSoup(resp.content, 'lxml')
                    return resp, soup
                return resp, None
            except Exception as e:
                logger.warning(f"Fetch attempt {attempt+1} failed for {url}: {e}")
                time.sleep(1 + attempt)
        return None, None

    # ── text extraction ───────────────────────────────────────────────────────

    def _extract_page_data(self, url: str, soup: BeautifulSoup) -> dict:
        """
        Extract structured key-value data from a page.
        Returns a dict with: title, description, headings, paragraphs, links,
                             dates, keywords, full_text
        """
        if soup is None:
            return {}

        # Remove nav/footer/script/style junk
        for tag in soup(['nav', 'footer', 'script', 'style', 'header', 'aside']):
            tag.decompose()

        title = (soup.find('title') or soup.find('h1') or soup.find('h2'))
        title_text = title.get_text(strip=True) if title else urlparse(url).path

        # Meta description
        meta_desc = ''
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            meta_desc = meta.get('content', '')

        # Headings hierarchy
        headings = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            txt = tag.get_text(strip=True)
            if txt and len(txt) > 3:
                headings.append({'level': tag.name, 'text': txt})

        # Main paragraph text
        paragraphs = []
        for p in soup.find_all('p'):
            txt = p.get_text(strip=True)
            if txt and len(txt) > 30:
                paragraphs.append(txt)

        # All text combined and cleaned
        full_text = ' '.join(soup.stripped_strings)
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        # Date patterns in text
        date_pattern = re.compile(
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|'
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4})\b',
            re.IGNORECASE
        )
        dates = list(set(date_pattern.findall(full_text)))[:10]

        # Keyword extraction (simple frequency)
        stop_words = {'the','a','an','and','or','of','to','in','is','it','be','are','was','for',
                     'this','that','with','from','have','has','at','by','on','as','but','not'}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', full_text.lower())
        freq = {}
        for w in words:
            if w not in stop_words:
                freq[w] = freq.get(w, 0) + 1
        keywords = sorted(freq, key=lambda x: -freq[x])[:20]

        # Outbound links
        links_out = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            text = a.get_text(strip=True)
            links_out.append({'url': href, 'text': text[:100]})

        return {
            'source_url': url,
            'title': title_text[:200],
            'description': meta_desc[:500],
            'headings': headings[:20],
            'paragraphs': paragraphs[:30],
            'dates_found': dates,
            'keywords': keywords,
            'full_text': full_text[:8000],
            'links': links_out[:50],
            'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'domain': urlparse(url).netloc,
        }

    # ── download binary files ─────────────────────────────────────────────────

    def _download_file(self, url: str, title: str, source_page: str) -> bool:
        if url in self.downloaded_urls:
            return False
        try:
            resp = self.session.get(url, stream=True, timeout=self.timeout, verify=False)
            resp.raise_for_status()

            filename = Path(urlparse(url).path).name or f"file_{self._url_slug(url)}.pdf"
            # sanitize
            filename = re.sub(r'[^\w.\-]', '_', filename)[:120]
            save_path = self.download_dir / filename
            if save_path.exists():
                save_path = self.download_dir / f"{save_path.stem}_{self._url_slug(url)}{save_path.suffix}"

            with open(save_path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            meta = {
                'source_url': url, 'source_page': source_page,
                'link_text': title, 'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            }
            save_path.with_suffix(save_path.suffix + '.meta.json').write_text(
                json.dumps(meta, indent=2)
            )
            self._save_to_history(url)
            logger.info(f"Downloaded binary: {save_path.name}")
            return True
        except Exception as e:
            logger.warning(f"Binary download failed for {url}: {e}")
            return False

    # ── save page record ──────────────────────────────────────────────────────

    def _save_page_record(self, data: dict) -> Path:
        slug = self._url_slug(data['source_url'])
        path = self.pages_dir / f"page_{slug}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return path

    # ── main crawl ────────────────────────────────────────────────────────────

    def crawl(
        self,
        start_urls: list,
        max_pages: int = 30,
        max_depth: int = 2,
        download_files: bool = True,
        on_page_saved=None,          # callback(page_data) for live indexing
    ) -> dict:
        """
        Crawl from start_urls up to max_pages pages (and optional file downloads).

        Returns:
            {
              'pages_scraped': int,
              'files_downloaded': int,
              'page_records': [path, ...],
            }
        """
        allowed_domains = {urlparse(u).netloc for u in start_urls} if self.same_domain_only else None

        visited: set = set()
        queue: deque = deque([(u, 0) for u in start_urls])
        pages_scraped = 0
        files_downloaded = 0
        page_records = []

        while queue and pages_scraped < max_pages:
            url, depth = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            ext = _url_ext(url)
            if ext in SKIP_EXTS:
                continue

            # Binary file to download
            if ext in DOWNLOAD_EXTS:
                if download_files:
                    if self._download_file(url, '', url):
                        files_downloaded += 1
                        time.sleep(self.rate_limit)
                continue

            # Domain restriction
            if allowed_domains and urlparse(url).netloc not in allowed_domains:
                continue

            logger.info(f"[depth={depth}] Crawling: {url}")
            resp, soup = self._fetch(url)
            if soup is None:
                continue

            self._rotate_ua()

            # Extract and save page data
            page_data = self._extract_page_data(url, soup)
            if page_data.get('full_text'):
                record_path = self._save_page_record(page_data)
                page_records.append(str(record_path))
                pages_scraped += 1
                self._save_to_history(url)

                if on_page_saved:
                    try:
                        on_page_saved(page_data)
                    except Exception as e:
                        logger.error(f"on_page_saved callback failed: {e}")

            # Enqueue children
            if depth < max_depth:
                for link_info in page_data.get('links', []):
                    child_url = link_info['url']
                    if child_url not in visited:
                        child_ext = _url_ext(child_url)
                        if child_ext not in SKIP_EXTS:
                            queue.append((child_url, depth + 1))

            time.sleep(self.rate_limit)

        logger.info(f"Crawl done. pages={pages_scraped}, files={files_downloaded}")
        return {
            'pages_scraped': pages_scraped,
            'files_downloaded': files_downloaded,
            'page_records': page_records,
        }


class NoticesCrawler(WebCrawler):
    """
    Legacy-compatible wrapper that reads from config.yaml
    and crawls the configured university URLs.
    """

    def __init__(self, config_path="config/config.yaml"):
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        base = Path(config_path).parent.parent
        download_dir = base / self.config['directories'].get('watch', 'data/watch')
        data_dir = base / "data"
        rate = self.config['scraping'].get('rate_limit', 1.5)
        timeout = self.config['scraping'].get('timeout', 12)
        retry = self.config['scraping'].get('retry_count', 2)

        super().__init__(
            download_dir=download_dir,
            data_dir=data_dir,
            rate_limit=rate,
            timeout=timeout,
            retry_count=retry,
        )
        self._config_start_urls = self.config['scraping'].get('target_urls', [])
        self._download_limit = self.config['scraping'].get('download_limit', 20)

    def crawl_config(self, limit=None, on_page_saved=None):
        """Crawl using config URLs."""
        result = self.crawl(
            start_urls=self._config_start_urls,
            max_pages=limit or self._download_limit,
            on_page_saved=on_page_saved,
        )
        return result['pages_scraped'] + result['files_downloaded']

    # keep old signature for backwards compat
    def crawl(self, start_urls=None, limit=None, max_pages=None, **kwargs):
        if isinstance(start_urls, int):
            # old API: crawl(limit=N)
            limit = start_urls
            start_urls = None

        if start_urls is None:
            start_urls = self._config_start_urls
        if max_pages is None:
            max_pages = limit or self._download_limit

        return super().crawl(start_urls=start_urls, max_pages=max_pages, **kwargs)


# Alias
NoticesScraper = NoticesCrawler
