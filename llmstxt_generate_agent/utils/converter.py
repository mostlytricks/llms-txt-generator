from markdownify import markdownify as md
from bs4 import BeautifulSoup

def html_to_markdown(html_content):
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove common distractions
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    
    # Convert remaining HTML to Markdown
    # Use heading_style='ATX' for standard # Headings
    markdown = md(str(soup), heading_style="ATX")
    
    # Remove excessive blank lines
    lines = markdown.splitlines()
    cleaned_lines = [line for line in lines if line.strip()]
    return "\n".join(cleaned_lines)
