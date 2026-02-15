import logging
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
from .base import BaseCrawler

logger = logging.getLogger(__name__)

class RecursiveCrawler(BaseCrawler):
    def __init__(self, base_url: str, max_pages: int = 500, max_depth: int = 5):
        super().__init__(base_url)
        self.max_pages = max_pages
        self.max_depth = max_depth

    def crawl(self):
        # Queue stores (url, depth)
        queue = deque([(self.base_url, 0)])
        
        # Mark start as seen
        seen_urls = {self.base_url}
        
        logger.info(f"Starting recursive crawl from {self.base_url}")
        
        while queue and len(self.visited) < self.max_pages:
            current_url, depth = queue.popleft()
            
            if depth > self.max_depth:
                continue
            
            content = self.fetch_page(current_url)
            if not content:
                continue
                
            self.pages[current_url] = content
            self.visited.add(current_url)
            logger.info(f"Crawled (Recursive): {current_url} (Depth {depth})")
            
            # Extract links
            soup = BeautifulSoup(content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Normalize
                full_url = urljoin(current_url, href)
                full_url, _ = urldefrag(full_url) # Remove #fragment
                
                if full_url not in seen_urls and self.is_valid_url(full_url):
                    seen_urls.add(full_url)
                    queue.append((full_url, depth + 1))
        
        return self.pages
