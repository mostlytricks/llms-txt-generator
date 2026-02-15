# LLMs.txt Generator Agent

A powerful AI agent built with **Google ADK** and **Gemini Flash** to automatically generate `llms.txt` and `llms-full.txt` documentation files from any website.

It supports:
- **Sitemap Discovery**: Automatically finds `sitemap.xml` (even at domain roots).
- **Prefix Filtering**: strict crawling of specific sub-paths (great for monorepos like LangChain).
- **Markdown Conversion**: Clean, readability-focused conversion.
- **Custom Output**: Configurable naming, versioning, and output directories.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/mostlytricks/llms-txt-generator.git
    cd llms-txt-generator
    ```

2.  **Install dependencies** (using `uv` is recommended):
    ```bash
    uv sync
    # Or simply:
    uv run pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file and add your Google API key:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

## Usage

### CLI (Command Line Interface)

The easiest way to use the generator is via the command line.

```bash
uv run python agent.py <URL> [OPTIONS]
```

**Options:**
- `URL`: The root URL of the documentation to crawl.
- `--name`: Service name for the output files (e.g., `adk-docs`).
- `--version`: Version string (default: `1.0.0`).
- `--out`: Output directory (default: `outputs`).

**Examples:**

*Generate for ADK Docs:*
```bash
uv run python agent.py https://google.github.io/adk-docs --name adk-docs
```

*Generate for LangChain (Python only):*
```bash
uv run python agent.py https://docs.langchain.com/oss/python/langchain/ --name langchain-python --version 0.1.0
```

### Programmatic Usage (ADK)

You can import the tool or agent into your own Python code.

```python
from agent import generate_llms_txt

# Direct tool usage
result = generate_llms_txt(
    url="https://google.github.io/adk-docs",
    service_name="adk-docs",
    version="1.0.0",
    output_dir="outputs"
)
print(result)
```

## Output Format

The agent generates two files in the `outputs/` directory:

1.  **`{name}-llms-v{version}.txt`**: A lightweight index file with metadata and a list of links.
2.  **`{name}-llms-full-v{version}.txt`**: A merged file containing the full Markdown content of all crawled pages, formatted for LLM consumption.

## License

Apache 2.0
