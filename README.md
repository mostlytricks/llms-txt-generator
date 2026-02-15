# LLMs.txt Generator Agent

A powerful, autonomous AI agent built with **Google ADK** and **Gemini Flash** that generates standard `llms.txt` documentation for any website.

It intelligently decides the best strategy:
1.  **Check Official**: First, it looks for an existing `/llms.txt`.
2.  **Sitemap Discovery**: If missing, it tries to find and crawl `sitemap.xml`.
3.  **Recursive Fallback**: If no sitemap is found, it falls back to smart recursive crawling.

## Features

- **Smart Strategy**: Auto-switching between Official -> Sitemap -> Recursive web crawling.
- **Prefix Isolation**: Strictly follows URL path prefixes (e.g., `.../docs/python/`) to avoid out-of-scope crawling.
- **Markdown Conversion**: Converts HTML to clean, LLM-friendly Markdown.
- **Standard Output**: Generates both `llms.txt` (index) and `llms-full.txt` (full content).

## Installation

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/mostlytricks/llms-txt-generator.git
    cd llms-txt-generator
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    # Or: pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file with your API key:
    ```bash
    GOOGLE_API_KEY=your_key_here
    ```

## Usage

### 1. CLI (Runner Pattern)
The agent now runs directly with a natural language prompt.

```bash
# General usage
uv run -m llmstxt_generate_agent.agent "Generate documentation for https://google.github.io/adk-docs"

# Specific instructions
uv run -m llmstxt_generate_agent.agent "Generate docs for https://strandsagents.com and name the service strands-agents"
```

### 2. Python Agent (Runner Pattern)
Integrate the agent into your ADK application using the Runner pattern for natural language control.

```python
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from llmstxt_generate_agent.agent import llms_txt_agent

async def main():
    runner = Runner(session_service=InMemorySessionService())
    
    # The agent understands natural language and will pick the right tools
    prompt = "Generate documentation for https://strandsagents.com"
    
    async for event in runner.run_async(llms_txt_agent, prompt):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

## Project Structure

- `llmstxt_generate_agent/`: Core package.
  - `agent.py`: Agent definition (`LlmAgent`).
  - `utils/`: Crawlers (`SitemapCrawler`, `RecursiveCrawler`), formatters, and converters.
- `tests/`: Verification scripts (`test_runner.py`, `test_usage.py`).
- `outputs/`: Generated documentation files.
- `real-llms-txt/`: Downloaded official documentation files.

## License
Apache 2.0
