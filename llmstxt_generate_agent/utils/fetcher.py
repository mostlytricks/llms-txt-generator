import requests
import os
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

def fetch_official_llms_txt(base_url: str, service_name: str, output_dir: str = "real-llms-txt") -> list[str]:
    """
    Checks for and downloads official llms.txt and llms-full.txt from the base URL.
    Returns a list of messages describing what was found.
    """
    os.makedirs(output_dir, exist_ok=True)
    messages = []
    
    # Common locations for llms.txt
    # Standard: /llms.txt and /llms-full.txt
    # Sometimes it might be at the root of the domain, or at the base_path.
    # We will check the provided base_url location.
    
    files_to_check = [
        ("llms.txt", f"{service_name}-official-llms.txt"),
        ("llms-full.txt", f"{service_name}-official-llms-full.txt")
    ]
    
    headers = {
        'User-Agent': 'LLMs.txt-Generator/1.0 (+https://github.com/mostlytricks/llms-txt-generator)'
    }

    for filename, save_name in files_to_check:
        target_url = urljoin(base_url if base_url.endswith('/') else base_url + '/', filename)
        try:
            logger.info(f"Checking for official {filename} at {target_url}")
            response = requests.get(target_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # Basic validation that it looks like text
                if 'text' in response.headers.get('Content-Type', '') or response.text.strip():
                    save_path = os.path.join(output_dir, save_name)
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    msg = f"FOUND and SAVED official {filename} to {save_path}"
                    logger.info(msg)
                    messages.append(msg)
                else:
                    logger.info(f"Found {target_url} but content-type was not text.")
            else:
                logger.debug(f"Official {filename} not found (Status {response.status_code})")
                
        except requests.RequestException as e:
            logger.warning(f"Error checking for {target_url}: {e}")

    return messages
