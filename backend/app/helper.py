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
    
    # Handle both dict and CrawledPage object formats
    def to_dict(page):
        if hasattr(page, 'url'):  # It's a CrawledPage object
            return {
                "url": page.url,
                "title": page.page_title,
                "description": page.page_description,
                "content": page.page_content
            }
        return page  # Already a dict
    
    pages_as_dicts = [to_dict(p) for p in crawled_pages]
    
    root_page = pages_as_dicts[0]
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
    for page in pages_as_dicts[1:]:
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
    bad_terms = ["login", "privacy", "terms", "cart", "faq"]
    if any(t in url_lower for t in bad_terms):
        return True
        
    # Exclude based on schemes like mailto, tel, etc.
    if any(url_lower.startswith(prefix) for prefix in ['mailto:', 'tel:', 'javascript:']):
        return True
            
    # Exclude based on common file extensions
    excluded_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.zip', '.mp4']
    if any(urlparse(url_lower).path.endswith(ext) for ext in excluded_extensions):
        return True
            
    # Exclude URLs that are just fragments (anchor-only links)
    if url_lower.startswith('#'):
        return True
    # Exclude URLs that are too deep (more than 3 levels of nested pages)
    if urlparse(url_lower).path.count("/") > 3:
        return True

    return False

def normalize_url(url: str) -> str:
    """
    Normalize URL to catch duplicates with slight variations.
    """
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Remove trailing slash and normalize
    path = parsed.path.rstrip('/') or '/'
    
    # Reconstruct normalized URL
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized

def calculate_page_score(depth: int) -> int:
    """
    Calculate page importance score based on depth.
    Closer to root = higher score.
    Future: Can be enhanced with LLM-based scoring.
    """
    return max(0, 100 - (depth * 10))

def is_valid_url(url: str) -> bool:
        """Validate URL format and scheme."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and parsed.netloc
        except Exception:
            return False

