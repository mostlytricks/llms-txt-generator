import sys
import os

# Ensure module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llmstxt_generate_agent.agent import generate_llms_txt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print(f"\n[Test 5] Strands Agents Verification")
    target_url_strands = "https://strandsagents.com/latest/documentation/docs/"
    service_name_strands = "strands-agents"
    
    result_strands = generate_llms_txt(
        url=target_url_strands,
        service_name=service_name_strands,
        version="1.0.0",
        output_dir="test_outputs"
    )
    print(result_strands)
