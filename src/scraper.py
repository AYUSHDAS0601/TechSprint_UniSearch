import requests
from bs4 import BeautifulSoup
import logging
import yaml
import json
import random
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
from collections import deque
from .utils import setup_logging

logger = setup_logging("Scraper")

# List of common User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

class NoticesCrawler:
    """Advanced web crawler for discovering and downloading university notices."""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.base_url = self.config['scraping']['base_url']
        self.download_dir = Path(self.config['directories']['watch'])
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.download_dir / "download_history.txt"
        self.downloaded_files = self._load_history()
        
        # Crawling settings
        self.retry_count = self.config['scraping'].get('retry_count', 3)
        self.timeout = self.config['scraping'].get('timeout', 10)
        self.max_depth = self.config['scraping'].get('max_depth', 2)
        self.rate_limit = self.config['scraping'].get('rate_limit', 1.0)
        
        # Crawl tracking
        self.visited_urls = set()
        self.queued_urls = set()
        
        # Initialize Session
        self.session = requests.Session()
        self._rotate_user_agent()
        
        # Domain restriction
        self.allowed_domain = urlparse(self.base_url).netloc

    def _rotate_user_agent(self):
        """Rotate User-Agent to mimic different browsers."""
        ua = random.choice(USER_AGENTS)
        self.session.headers.update({
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        logger.debug(f"Rotated User-Agent to: {ua[:50]}...")

    def _load_history(self):
        """Load previously downloaded file URLs."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return set(f.read().splitlines())
        return set()

    def _save_history(self, url):
        """Save downloaded URL to history."""
        with open(self.history_file, 'a') as f:
            f.write(f"{url}\n")
        self.downloaded_files.add(url)

    def crawl(self, limit=None, start_urls=None):
        """
        Main crawling method with BFS-style recursive discovery.
        
        Args:
            limit: Maximum number of files to download
            start_urls: List of seed URLs to start crawling from
        """
        # Initialize with target URLs from config or provided start URLs
        if start_urls:
            seed_urls = start_urls
        else:
            seed_urls = self.config['scraping'].get('target_urls', [self.base_url])
        
        logger.info(f"Starting crawl from {len(seed_urls)} seed URL(s)")
        
        # BFS queue: (url, depth)
        queue = deque([(url, 0) for url in seed_urls])
        
        limit = limit or self.config['scraping']['download_limit']
        download_count = 0
        
        while queue and download_count < limit:
            current_url, depth = queue.popleft()
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
                
            # Skip if exceeds max depth
            if depth > self.max_depth:
                logger.debug(f"Skipping {current_url} (depth {depth} > max {self.max_depth})")
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            logger.info(f"Crawling [{depth}/{self.max_depth}]: {current_url}")
            
            # Fetch page
            soup = self._fetch_page(current_url)
            if not soup:
                continue
            
            # Find all links on the page
            links = soup.find_all('a', href=True)
            
            for link in links:
                if download_count >= limit:
                    break
                
                href = link['href']
                full_url = urljoin(current_url, href)
                link_text = link.get_text(strip=True)
                
                # Check domain restriction
                if not self._is_same_domain(full_url):
                    continue
                
                # Check if it's a downloadable file
                if self._is_file_url(full_url):
                    if full_url not in self.downloaded_files:
                        if self._download_file(full_url, link_text, current_url):
                            download_count += 1
                            logger.info(f"Downloaded {download_count}/{limit} files")
                            time.sleep(self.rate_limit)
                
                # If it's a page link, add to crawl queue
                elif self._is_relevant_page(link_text, full_url):
                    if full_url not in self.visited_urls and full_url not in self.queued_urls:
                        queue.append((full_url, depth + 1))
                        self.queued_urls.add(full_url)
                        logger.debug(f"Queued: {full_url} (depth {depth + 1})")
            
            # Rate limiting between page fetches
            time.sleep(self.rate_limit)
        
        logger.info(f"Crawl complete. Downloaded {download_count} files, visited {len(self.visited_urls)} pages")
        return download_count

    def _is_same_domain(self, url):
        """Check if URL is from the same domain."""
        return urlparse(url).netloc == self.allowed_domain

    def _is_file_url(self, url):
        """Check if URL points to a downloadable file."""
        return url.lower().endswith(('.pdf', '.jpg', '.png', '.jpeg', '.doc', '.docx', '.xls', '.xlsx'))

    def _is_relevant_page(self, text, url):
        """
        Determine if a link is worth crawling for more content.
        Uses keyword matching to find notice/exam pages.
        """
        text = text.lower()
        url = url.lower()
        
        # Ignore common navigation/footer links
        ignore_terms = [
            'privacy', 'terms', 'copyright', 'contact', 'login', 
            'signup', 'register', 'home', 'about', 'careers',
            'facebook', 'twitter', 'instagram', 'linkedin'
        ]
        if any(term in text for term in ignore_terms):
            return False
        
        # Prioritize notice-related keywords
        relevant_keywords = [
            'notice', 'exam', 'circular', 'announcement', 
            'schedule', 'result', 'admission', 'semester',
            'news', 'event', 'academic', 'student'
        ]
        
        # Check both text and URL path for keywords
        if any(kw in text for kw in relevant_keywords):
            return True
        if any(kw in url for kw in relevant_keywords):
            return True
        
        return False

    def _fetch_page(self, url):
        """Fetch and parse a web page with retry logic."""
        for attempt in range(self.retry_count):
            try:
                # Disable SSL verify for robustness
                response = self.session.get(url, timeout=self.timeout, verify=False)
                response.raise_for_status()
                
                # Only parse HTML content
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    logger.debug(f"Skipping non-HTML content: {content_type}")
                    return None
                
                return BeautifulSoup(response.content, 'lxml')
                
            except Exception as e:
                logger.warning(f"Fetch error ({attempt+1}/{self.retry_count}) for {url}: {e}")
                time.sleep(2 * (attempt + 1))
        
        return None

    def _download_file(self, url, title, source_page):
        """Download a file with metadata."""
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Downloading: {title[:40] if title else 'Untitled'}... ({url})")
                
                response = self.session.get(url, stream=True, timeout=self.timeout, verify=False)
                response.raise_for_status()
                
                # Generate filename
                filename = Path(url).name or f"download_{int(time.time())}.pdf"
                save_path = self.download_dir / filename
                
                # Avoid overwriting existing files
                if save_path.exists():
                    save_path = self.download_dir / f"{save_path.stem}_{int(time.time())}{save_path.suffix}"
                
                # Download file
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Save metadata
                meta = {
                    "source_url": url,
                    "source_page": source_page,
                    "original_link_text": title,
                    "scraped_at": time.time(),
                    "headers": dict(response.headers)
                }
                meta_path = save_path.with_suffix(save_path.suffix + ".meta.json")
                with open(meta_path, 'w') as f:
                    json.dump(meta, f, indent=2, default=str)
                
                self._save_history(url)
                logger.info(f"✓ Saved: {save_path.name}")
                return True
                
            except Exception as e:
                logger.warning(f"Download error ({attempt+1}/{self.retry_count}): {e}")
                time.sleep(2 * (attempt + 1))
        
        return False

# Backwards compatibility alias
NoticesScraper = NoticesCrawler

if __name__ == "__main__":
    # Test the crawler
    import logging
    logging.basicConfig(level=logging.INFO)
    
    crawler = NoticesCrawler()
    print("Starting web crawler...")
    downloaded = crawler.crawl(limit=10)
    print(f"Crawling complete. Downloaded {downloaded} files.")
