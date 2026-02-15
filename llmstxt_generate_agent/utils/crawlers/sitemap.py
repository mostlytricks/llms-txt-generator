import xml.etree.ElementTree as ET
import logging
from urllib.parse import urlparse
from .base import BaseCrawler

logger = logging.getLogger(__name__)

class SitemapCrawler(BaseCrawler):
    def get_sitemap_urls(self):
        """
        Try to find sitemaps in 5 common locations/ways:
        1. base_url/sitemap.xml
        2. base_url/sitemap_index.xml
        3. domain_root/sitemap.xml
        4. domain_root/sitemap_index.xml
        5. robots.txt Sitemap: directive
        """
        
        candidates = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{urlparse(self.base_url).scheme}://{self.domain}/sitemap.xml",
            f"{urlparse(self.base_url).scheme}://{self.domain}/sitemap_index.xml"
        ]
        
        # Add candidates from robots.txt
        robots_url = f"{urlparse(self.base_url).scheme}://{self.domain}/robots.txt"
        robots_content = self.fetch_page(robots_url)
        if robots_content:
            for line in robots_content.splitlines():
                if line.lower().startswith('sitemap:'):
                    candidates.append(line.split(':', 1)[1].strip())

        # Deduplicate
        candidates = list(dict.fromkeys(candidates))
        
        valid_urls = []
        found_sitemap = False

        for sitemap_url in candidates:
            # Avoid re-checking if we already found a good sitemap, 
            # OR we can check all to be comprehensive. 
            # Let's check until we find something, but sitemap_index might point to others.
            # For simplicity, we'll try until we find *some* URLs.
            if found_sitemap and valid_urls:
                 break

            logger.info(f"Checking for sitemap at: {sitemap_url}")
            content = self.fetch_page(sitemap_url)
            if not content:
                continue
                
            try:
                # Basic check if it's XML-ish
                if not content.strip().startswith('<'):
                     continue
                     
                root = ET.fromstring(content)
                # Handle standard namespaces
                namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                # Check for sitemapindex FIRST
                if 'sitemapindex' in root.tag:
                    logger.info(f"Found sitemap index at {sitemap_url}, recursing...")
                    for sitemap_tag in root.findall('.//ns:sitemap', namespaces) or root.findall('.//sitemap'):
                        loc = sitemap_tag.find('ns:loc', namespaces) if root.find('.//ns:sitemap', namespaces) else sitemap_tag.find('loc')
                        if loc is not None and loc.text:
                            # Recurse (simple 1-level for now to avoid infinite loops)
                            sub_sitemap_url = loc.text.strip()
                            sub_content = self.fetch_page(sub_sitemap_url)
                            if sub_content:
                                try:
                                    sub_root = ET.fromstring(sub_content)
                                    valid_urls.extend(self._parse_urlset(sub_root, namespaces))
                                    found_sitemap = True
                                except:
                                    pass
                else:
                    # Regular urlset
                    urls = self._parse_urlset(root, namespaces)
                    if urls:
                        valid_urls.extend(urls)
                        found_sitemap = True

            except ET.ParseError as e:
                logger.warning(f"Failed to parse sitemap at {sitemap_url}: {e}")
                
        return valid_urls

    def _parse_urlset(self, root, namespaces):
        urls = []
        for url_tag in root.findall('.//ns:url', namespaces) or root.findall('.//url'):
            loc = url_tag.find('ns:loc', namespaces) if root.find('.//ns:url', namespaces) else url_tag.find('loc')
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
        return urls

    def crawl(self):
        all_urls = self.get_sitemap_urls()
        
        # Filter URLs to match the base_url prefix
        filtered_urls = [u for u in all_urls if self.is_valid_url(u)]
        
        logger.info(f"Sitemap: Found {len(all_urls)} URLs, {len(filtered_urls)} matched prefix {self.base_url}")
        
        for url in filtered_urls:
             # Basic safety
            if url in self.visited:
                continue

            content = self.fetch_page(url)
            if content:
                self.pages[url] = content
                self.visited.add(url)
                logger.info(f"Crawled: {url}")
        
        return self.pages
