def format_llms_txt(title, description, pages_info):
    """
    Generates content for llms.txt
    
    Args:
        title (str): Project title (H1)
        description (str): Project description (Blockquote)
        pages_info (list of dict): List of pages with 'url', 'title', 'description'
        
    Returns:
        str: Content of llms.txt
    """
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> {description}")
    lines.append("")
    lines.append("## Documentation")
    lines.append("")
    
    for page in pages_info:
        url = page['url']
        title = page.get('title', url) # fallback to url if no title
        desc = page.get('description', '')
        
        line = f"- [{title}]({url})"
        if desc:
             line += f": {desc}"
        lines.append(line)
        
    lines.append("")
    lines.append("## Optional")
    lines.append("- [Full Documentation](llms-full.txt): Comprehensive documentation in a single file.")
    
    return "\n".join(lines)

def format_llms_full_txt(title, content_map):
    """
    Generates content for llms-full.txt
    
    Args:
        title (str): Project title
        content_map (dict): url -> markdown_content
        
    Returns:
        str: Content of llms-full.txt
    """
    lines = []
    lines.append(f"# {title} - Full Documentation")
    lines.append("")
    
    for url, content in content_map.items():
        lines.append(f"## Page: {url}")
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")
        
    return "\n".join(lines)
