import asyncio
import logging
import sys
import traceback
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Ensure module is found
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llmstxt_generate_agent.agent import llms_txt_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_NAME = "llms_txt_gen_app"
USER_ID = "test_user"
SESSION_ID = "test_session_01"

async def main():
    print("--- Setting up Runner ---")
    
    # 1. Setup Session Service
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    
    # 2. Setup Runner
    # Note: Runner constructor signature might vary slightly depending on version, 
    # but typically: Runner(agent, app_name, session_service)
    runner = Runner(
        agent=llms_txt_agent, 
        app_name=APP_NAME, 
        session_service=session_service
    )
    
    # 3. Create Prompt
    prompt_text = (
        "Please generate documentation for the Google ADK. "
        "The documentation is located at https://google.github.io/adk-docs "
        "and I want the output files to be named 'adk-docs-runner'."
    )
    
    content = types.Content(role="user", parts=[types.Part(text=prompt_text)])
    
    print(f"\n--- Sending Prompt ---\n{prompt_text}\n")
    
    try:
        # 4. Run Async
        print("Running agent via Runner...")
        async for event in runner.run_async(
            user_id=USER_ID, 
            session_id=SESSION_ID, 
            new_message=content
        ):
            # Print event details for debugging/verification
            print(f"Event: {event.id} ({event.author})")
            
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Text: {part.text[:100]}...")
                    if part.function_call:
                        print(f"Tool Call: {part.function_call.name}")
                    if part.function_response:
                        print(f"Tool Result: {part.function_response.name}")
            
            if event.is_final_response() and event.content and event.content.parts:
                 print(f"\n==> FINAL RESPONSE: {event.content.parts[0].text}")

    except Exception as e:
        print(f"Error executing runner: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
