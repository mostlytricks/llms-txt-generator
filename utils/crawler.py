import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(self.base_url).netloc
        self.visited = set()
        self.pages = {}  # url -> content (html)

    def fetch_page(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def get_sitemap_urls(self):
        # Ensure we look for sitemap at the end of the path, not replacing the last segment
        sitemap_url = self.base_url + '/sitemap.xml'
        content = self.fetch_page(sitemap_url)
        if not content:
            logger.warning("No sitemap found at default location.")
            return []
        
        try:
            root = ET.fromstring(content)
            # Handle standard sitemap namespaces if present
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = []
            for url_tag in root.findall('.//ns:url', namespaces) or root.findall('.//url'):
                loc = url_tag.find('ns:loc', namespaces) if root.find('.//ns:url', namespaces) else url_tag.find('loc')
                if loc is not None and loc.text:
                   urls.append(loc.text.strip())
            return urls
        except ET.ParseError as e:
            logger.error(f"Failed to parse sitemap: {e}")
            return []

    def crawl(self):
        urls = self.get_sitemap_urls()
        
        if not urls:
            logger.info("Falling back to recursive crawl (not fully implemented yet, just base url).")
            urls = [self.base_url]
            # Todo: implement recursive crawl if needed, but sitemap is preferred.
        
        logger.info(f"Found {len(urls)} pages to crawl.")

        for url in urls:
            if url in self.visited:
                continue
            
            # Simple filter to keep within domain and ignore non-html
            if self.domain not in url:
                continue
            
            # Optional: Filter out assets
            if any(url.endswith(ext) for ext in ['.png', '.jpg', '.css', '.js', '.xml', '.json']):
                continue

            content = self.fetch_page(url)
            if content:
                self.pages[url] = content
                self.visited.add(url)
                logger.info(f"Crawled: {url}")
        
        return self.pages
