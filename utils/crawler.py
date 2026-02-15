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
        # 1. Try base_url + /sitemap.xml
        sitemap_urls = [
            self.base_url + '/sitemap.xml',
            f"{urlparse(self.base_url).scheme}://{self.domain}/sitemap.xml"
        ]
        
        # Deduplicate while preserving order
        sitemap_urls = list(dict.fromkeys(sitemap_urls))

        for sitemap_url in sitemap_urls:
            logger.info(f"Checking for sitemap at: {sitemap_url}")
            content = self.fetch_page(sitemap_url)
            if content:
                try:
                    root = ET.fromstring(content)
                    # Handle standard sitemap namespaces if present
                    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    urls = []
                    for url_tag in root.findall('.//ns:url', namespaces) or root.findall('.//url'):
                        loc = url_tag.find('ns:loc', namespaces) if root.find('.//ns:url', namespaces) else url_tag.find('loc')
                        if loc is not None and loc.text:
                           urls.append(loc.text.strip())
                    
                    if urls:
                        logger.info(f"Found {len(urls)} URLs in sitemap: {sitemap_url}")
                        return urls
                except ET.ParseError as e:
                    logger.error(f"Failed to parse sitemap at {sitemap_url}: {e}")
        
        logger.warning("No sitemap found at checked locations.")
        return []

    def crawl(self):
        urls = self.get_sitemap_urls()
        
        if not urls:
            logger.info("Falling back to recursive crawl (not fully implemented yet, just base url).")
            urls = [self.base_url]
            # Todo: implement recursive crawl if needed, but sitemap is preferred.
        
        logger.info(f"Found {len(urls)} candidates in sitemap.")

        filtered_urls = []
        for url in urls:
             # Normalize URL (strip trailing slash for comparison consistency if needed, 
             # but strictly startswith is usually best for directory separation)
             if url.startswith(self.base_url):
                 filtered_urls.append(url)
        
        logger.info(f"Filtered to {len(filtered_urls)} pages under {self.base_url}")

        for url in filtered_urls:
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
