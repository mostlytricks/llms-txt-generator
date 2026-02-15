import os
import logging
from agent import generate_llms_txt

# Configure logging to see the crawler's progress
logging.basicConfig(level=logging.INFO)

def run_demo():
    print("--- Starting Demo Generation ---")
    
    # Example: Generating docs for a small section or a reliable documentation site
    # (We use ADK docs again here for a quick consistent test)
    target_url = "https://google.github.io/adk-docs/visual-builder/"
    service_name = "adk-visual-builder-demo"
    version = "0.0.1"
    output_dir = "test_outputs"
    
    print(f"Target: {target_url}")
    print(f"Output: {output_dir}/{service_name}-llms-v{version}.txt")
    
    result = generate_llms_txt(
        url=target_url,
        service_name=service_name,
        version=version,
        output_dir=output_dir
    )
    
    print("\n--- Result ---")
    print(result)
    
    # Parse and print a snippet of the result to verify
    llms_file = os.path.join(output_dir, f"{service_name}-llms-v{version}.txt")
    if os.path.exists(llms_file):
        print("\n--- Generated File Snippet ---")
        with open(llms_file, 'r', encoding='utf-8') as f:
            print(f.read()[:200])
        print("...\n(File content truncated)")
    else:
        print("Error: Output file not found.")

if __name__ == "__main__":
    run_demo()
