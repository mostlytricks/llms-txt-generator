import os
import sys
import logging

# Ensure module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llmstxt_generate_agent.agent import generate_llms_txt

# Configure logging to see the crawler's progress
logging.basicConfig(level=logging.INFO)

def run_demo():
    print("--- Starting Demo Generation ---")
    
    # 1. Standard Test (Sitemap Preferred)
    print(f"\n[Test 1] Standard Sitemap Strategy")
    target_url = "https://google.github.io/adk-docs/visual-builder/"
    service_name = "adk-visual-builder-sitemap"
    version = "0.0.1"
    output_dir = "test_outputs"
    print(f"Target: {target_url}")
    
    result = generate_llms_txt(
        url=target_url,
        service_name=service_name,
        version=version,
        output_dir=output_dir
    )
    print(result)

    # 2. Recursive Test (Forced)
    print(f"\n[Test 2] Recursive Strategy (Forced)")
    service_name_rec = "adk-visual-builder-recursive"
    
    result_rec = generate_llms_txt(
        url=target_url,
        service_name=service_name_rec,
        version=version,
        output_dir=output_dir,
        ignore_sitemap=True
    )
    print(result_rec)

    # 3. Official LLMs.txt Test
    print(f"\n[Test 3] Official LLMs.txt Fetching")
    target_url_official = "https://openai.github.io/openai-agents-python/"
    service_name_official = "openai-agents-python"
    
    result_official = generate_llms_txt(
        url=target_url_official,
        service_name=service_name_official,
        version=version,
        output_dir=output_dir
    )
    print(result_official)

    # 4. Agent Class Verification
    print(f"\n[Test 4] LlmAgent Class Verification")
    from llmstxt_generate_agent.agent import get_agent
    from google.adk.agents.llm_agent import LlmAgent
    
    agent = get_agent()
    print(f"Agent Type: {type(agent).__name__}")
    
    try:
        if isinstance(agent, LlmAgent):
            print("SUCCESS: Agent is instance of LlmAgent")
        else:
            print(f"FAILURE: Agent is {type(agent)}")
    except Exception as e:
        print(f"Verification Skipped (Import issue?): {e}")

    # 5. Strands Agents Verification
    print(f"\n[Test 5] Strands Agents Verification")
    target_url_strands = "https://strandsagents.com/latest/documentation/docs/"
    service_name_strands = "strands-agents"
    
    result_strands = generate_llms_txt(
        url=target_url_strands,
        service_name=service_name_strands,
        version=version,
        output_dir=output_dir
    )
    print(result_strands)


    
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
