import hashlib
from .core.config import settings
from urllib.parse import urlparse

def categorize_url(url: str) -> str:
    """Heuristic section categorization based on URL path."""
    u = url.lower()
    if "doc" in u:
        return "Docs"
    if "example" in u or "demo" in u:
        return "Examples"
    if "blog" in u or "post" in u:
        return "Blog"
    return "Other"

def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def generate_llms_txt(crawled_pages: list, root_url: str) -> str:
    """Aggregate crawled pages into one compliant llms.txt."""
    if not crawled_pages:
        return ""

    root_page = crawled_pages[0]
    title = root_page.get("title") or root_url
    desc = root_page.get("description", "")
    lines = [f"# {title}\n"]

    if desc:
        lines.append(f"> {desc}\n")

    lines.append(
        f"This document lists key resources discovered from {root_url}. "
        f"Only top-level pages (depth ≤ {settings.MAX_DEPTH}) are included.\n"
    )

    # Group by section
    sections = {}
    for page in crawled_pages[1:]:
        section = categorize_url(page["url"])
        sections.setdefault(section, []).append(page)

    for section, pages in sections.items():
        lines.append(f"## {section}\n")
        for p in pages:
            link_text = p["title"] or p["url"]
            notes = p.get("description") or p.get("content", "")
            note_suffix = f": {notes}" if notes else ""
            lines.append(f"- [{link_text}]({p['url']}){note_suffix}")

    return "\n".join(lines)

def is_excluded_url(url: str) -> bool:
    """Check if URL should be excluded from crawling based on scheme or extension."""
    url_lower = url.lower()
        
    # Exclude based on schemes like mailto, tel, etc.
    if any(url_lower.startswith(prefix) for prefix in ['mailto:', 'tel:', 'javascript:']):
        return True
            
    # Exclude based on common file extensions
    excluded_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.zip', '.mp4']
    if any(urlparse(url_lower).path.endswith(ext) for ext in excluded_extensions):
        return True
            
    # Exclude URLs that are just fragments (anchor-only links)
    if url.startswith('#'):
        return True

    return False

def normalize_url(url: str) -> str:
    """
    Normalize URL to catch duplicates with slight variations.
    """
    from urllib.parse import urlparse
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Remove trailing slash and normalize
    path = parsed.path.rstrip('/') or '/'
    
    # Reconstruct normalized URL
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized