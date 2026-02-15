from google.adk.agents.llm_agent import LlmAgent
# from google.adk import Agent # No longer needed if using LlmAgent directly
# from google.adk.model import Model # Not importing Model for now if passing string
# from google.adk import tool # Not finding 'tool', assuming plain function works

from .utils.crawlers import SitemapCrawler, RecursiveCrawler
from .utils.converter import html_to_markdown
from .utils.formatter import format_llms_txt, format_llms_full_txt
from .utils.fetcher import fetch_official_llms_txt
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import os
from dotenv import load_dotenv

# ... (unchanged helper functions and tools) ...

# --- Agent Setup ---





# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def _derive_service_name(url: str, service_name: str = None) -> str:
    if service_name:
        return service_name
    parsed_url = urlparse(url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    if path_parts:
        return path_parts[-1]
    return parsed_url.netloc.replace('.', '-')

def _process_and_save_pages(pages: dict, url: str, service_name: str, version: str, output_dir: str) -> str:
    """Internal helper to process crawled pages and save them."""
    if not pages:
        return f"No pages found for {url}."
    
    logger.info(f"Crawled {len(pages)} pages.")
    
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
        
    # Format and Save
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

# --- Tools ---

def check_official_docs(url: str, service_name: str = None) -> str:
    """
    Checks if the target website already provides an official `llms.txt`.
    Downloads it to `real-llms-txt/` if found.
    
    Args:
        url: The root URL of the documentation.
        service_name: Optional name for saving the file.
    """
    service_name = _derive_service_name(url, service_name)
    msgs = fetch_official_llms_txt(url, service_name)
    if msgs:
        return "\n".join(msgs)
    return "No official llms.txt found at standard locations."

def generate_via_sitemap(url: str, service_name: str = None, version: str = "1.0.0", output_dir: str = "outputs") -> str:
    """
    Generates documentation by discovering and crawling sitemaps.
    Use this method FIRST for generation.
    """
    service_name = _derive_service_name(url, service_name)
    logger.info(f"Attempting sitemap crawl for {url}")
    
    crawler = SitemapCrawler(url)
    pages = crawler.crawl()
    
    if not pages:
        return f"Sitemap crawl failed: No pages found for {url}. Please try recursive generation."
        
    return _process_and_save_pages(pages, url, service_name, version, output_dir)

def generate_via_recursion(url: str, service_name: str = None, version: str = "1.0.0", output_dir: str = "outputs") -> str:
    """
    Generates documentation by recursively crawling links (spidering).
    Use this ONLY if sitemap generation fails.
    """
    service_name = _derive_service_name(url, service_name)
    logger.info(f"Starting recursive crawl for {url}")
    
    crawler = RecursiveCrawler(url)
    pages = crawler.crawl()
    
    return _process_and_save_pages(pages, url, service_name, version, output_dir)

# --- Facade for CLI Compatibility ---

def generate_llms_txt(url: str, service_name: str = None, version: str = "1.0.0", output_dir: str = "outputs", ignore_sitemap: bool = False) -> str:
    """
    Orchestrator function (Facade) that mimics the agent's decision logic for CLI usage.
    """
    msgs = []
    
    # 0. Official Check
    official_res = check_official_docs(url, service_name)
    msgs.append(f"[Official Check]: {official_res}")
    
    # 1. Strategy Selection
    if ignore_sitemap:
        res = generate_via_recursion(url, service_name, version, output_dir)
        msgs.append(f"[Recursive]: {res}")
    else:
        # Try Sitemap
        res = generate_via_sitemap(url, service_name, version, output_dir)
        if "failed" in res.lower() or "no pages" in res.lower():
            msgs.append(f"[Sitemap]: {res}")
            msgs.append("[Fallback]: Switching to recursive strategy...")
            res_rec = generate_via_recursion(url, service_name, version, output_dir)
            msgs.append(f"[Recursive]: {res_rec}")
        else:
            msgs.append(f"[Sitemap]: {res}")
            
    return "\n\n".join(msgs)



# --- Agent Instance ---
# Defined here to ensure all tools are loaded first

# --- Agent Instance ---
# Defined here to ensure all tools are loaded first

description = "You are an expert AI documentation assistant specializing in the `llms.txt` standard."

instruction = (
    "Your goal is to provide `llms.txt` documentation. "
    "Follow this STRICT workflow:\n"
    "1. ALWAYS call `check_official_docs` first. If official docs exist, you are done (report success).\n"
    "2. If not, call `generate_via_sitemap`. This is the preferred generation method.\n"
    "3. ONLY if sitemap generation returns 'failed' or 'no pages', call `generate_via_recursion` as a fallback.\n"
    "Do not skip steps. Prioritize official sources, then sitemaps, then spidering.\n"
    "IMPORTANT: ALWAYS set `output_dir='outputs'` in your tool calls. Do not create other directories."
)

llms_txt_agent = LlmAgent(
    name="llms_txt_generator",
    model="gemini-flash-latest",
    tools=[check_official_docs, generate_via_sitemap, generate_via_recursion],
    description=description,
    instruction=instruction
)

if __name__ == "__main__":
    import asyncio
    import sys
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: uv run -m llmstxt_generate_agent.agent \"<prompt>\"")
            sys.exit(1)
            
        prompt_text = sys.argv[1]
        print(f"--- Starting Agent with Prompt: {prompt_text} ---")
        
        APP_NAME = "llms_txt_cli"
        USER_ID = "cli_user"
        SESSION_ID = "cli_session"
        
        session_service = InMemorySessionService()
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        
        runner = Runner(agent=llms_txt_agent, app_name=APP_NAME, session_service=session_service)
        
        content = types.Content(role="user", parts=[types.Part(text=prompt_text)])
        
        try:
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                         if part.text:
                            print(part.text)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run(main())
