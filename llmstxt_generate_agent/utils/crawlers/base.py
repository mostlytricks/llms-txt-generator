import requests
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class BaseCrawler:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(self.base_url).netloc
        self.visited = set()
        self.pages = {} # url -> content (html)

    def fetch_page(self, url: str) -> str | None:
        try:
            # Basic header to avoid some bot detection, though sophisticated ones will still block
            headers = {
                'User-Agent': 'LLMs.txt-Generator/1.0 (+https://github.com/mostlytricks/llms-txt-generator)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def is_valid_url(self, url: str) -> bool:
        """Checks if URL is within scope and not an asset."""
        if not url.startswith(self.base_url):
            return False
            
        if self.domain not in url:
            return False

        # Filter out assets
        if any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.xml', '.json', '.pdf', '.svg', '.zip']):
            return False
            
        return True
