from google.adk import Agent
# from google.adk.model import Model # Not importing Model for now if passing string
# from google.adk import tool # Not finding 'tool', assuming plain function works

from utils.crawler import Crawler
from utils.converter import html_to_markdown
from utils.formatter import format_llms_txt, format_llms_full_txt
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_llms_txt(url: str, service_name: str = None, version: str = "1.0.0", output_dir: str = "outputs") -> str:
    """
    Generates llms.txt and llms-full.txt from a given documentation URL.
    
    Args:
        url: The root URL of the documentation (e.g., https://google.github.io/adk-docs)
        service_name: Optional name of the service (e.g., adk-docs). If not provided, derived from URL.
        version: Version string for the output filenames (default: 1.0.0).
        output_dir: The directory to save the generated files (default: outputs).
        
    Returns:
        A message indicating success or failure.
    """
    logger.info(f"Starting generation for {url}")
    
    # Derive service name if not provided
    if not service_name:
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        if path_parts:
            service_name = path_parts[-1]
        else:
            service_name = parsed_url.netloc.replace('.', '-')
    
    # 1. Crawl
    crawler = Crawler(url)
    pages = crawler.crawl()
    
    if not pages:
        return f"No pages found for {url}."
    
    logger.info(f"Crawled {len(pages)} pages.")
    
    # 2. Process Pages
    processed_pages = []
    full_content_map = {}
    
    # Try to find a main title from the base URL page
    project_title = service_name
    project_description = "Documentation for the project."
    
    if url in pages:
        soup = BeautifulSoup(pages[url], 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            project_title = title_tag.get_text().strip()
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            project_description = meta_desc['content'].strip()

    for page_url, html in pages.items():
        # Convert to Markdown
        markdown = html_to_markdown(html)
        full_content_map[page_url] = markdown
        
        # Extract metadata for llms.txt
        soup = BeautifulSoup(html, 'html.parser')
        
        page_title = page_url
        title_tag = soup.find('title')
        if title_tag:
            page_title = title_tag.get_text().strip()
            
        page_desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            page_desc = meta_desc['content'].strip()
        
        processed_pages.append({
            'url': page_url,
            'title': page_title,
            'description': page_desc
        })
        
    # 3. Format and Save
    llms_txt_content = format_llms_txt(project_title, project_description, processed_pages)
    llms_full_txt_content = format_llms_full_txt(project_title, full_content_map)
    
    os.makedirs(output_dir, exist_ok=True)
    
    llms_filename = f"{service_name}-llms-v{version}.txt"
    llms_full_filename = f"{service_name}-llms-full-v{version}.txt"
    
    llms_path = os.path.join(output_dir, llms_filename)
    llms_full_path = os.path.join(output_dir, llms_full_filename)
    
    with open(llms_path, "w", encoding="utf-8") as f:
        f.write(llms_txt_content)
        
    with open(llms_full_path, "w", encoding="utf-8") as f:
        f.write(llms_full_txt_content)
        
    return f"Successfully generated {llms_filename} and {llms_full_filename} in {output_dir}"

# ADK Agent Setup
def get_agent():
    # Note: In a real ADK app, you might configure the model here.
    # For this specific task, the logic is self-contained in the tool, 
    # so the model is used primarily for the agent's conversational interface 
    # if we were to chat with it.
    
    agent = Agent(
        name="llms-txt-generator",
        model="gemini-1.5-flash-latest", # Or user's preferred model
        tools=[generate_llms_txt],
        system_prompt="You are a helpful assistant that can generate llms.txt files from documentation websites using the generate_llms_txt tool."
    )
    return agent

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate llms.txt and llms-full.txt from documentation URL.")
    parser.add_argument("url", help="The root URL of the documentation")
    parser.add_argument("--name", help="Service name (e.g. adk-docs)", default=None)
    parser.add_argument("--version", help="Version string (e.g. 1.0.0)", default="1.0.0")
    parser.add_argument("--out", help="Output directory", default="outputs")
    
    args = parser.parse_args()
    
    result = generate_llms_txt(args.url, service_name=args.name, version=args.version, output_dir=args.out)
    print(result)
