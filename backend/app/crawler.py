import logging
import traceback
from collections import deque
from typing import Dict, List, Set, Optional
from urllib.parse import urljoin, urlparse
from urllib import robotparser
import requests
from playwright.sync_api import sync_playwright, Browser
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
import datetime

from .helper import generate_llms_txt, get_text_hash, is_excluded_url
from .core.config import settings
from .database import SessionLocal
from .models import URLJob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## CHANGED: Moved constants here for easier configuration
REQUESTS_TIMEOUT = 10
PLAYWRIGHT_TIMEOUT = 60000
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


class WebCrawler:
    """Standardized web crawler instance to handle fallback"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self._browser: Optional[Browser] = None
        ## CHANGED: Added a robot parser instance
        self.robot_parser = robotparser.RobotFileParser()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources."""
        if self._browser:
            self._browser.close()
            self._browser = None
        self.session.close()

    ## CHANGED: Added method to prepare the robot parser for a specific domain
    def setup_robot_parser(self, root_url: str):
        """Fetches and parses the robots.txt file for the given domain."""
        robots_url = urljoin(root_url, "robots.txt")
        self.robot_parser.set_url(robots_url)
        try:
            self.robot_parser.read()
            logger.info(f"Successfully parsed robots.txt for {root_url}")
        except Exception as e:
            logger.warning(f"Could not read robots.txt for {root_url}: {e}")

    def _get_browser(self) -> Browser:
        if not self._browser:
            playwright = sync_playwright().start()
            self._browser = playwright.firefox.launch(headless=True)
        return self._browser
    
    def fetch_page_content(self, url: str) -> Dict[str, str]:
        """
        Fetch page content with requests first, fallback to Playwright.
        Returns dict with url, title, and html.
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
            
        ## CHANGED: Check robots.txt before fetching
        if not self.robot_parser.can_fetch(USER_AGENT, url):
            raise Exception(f"Crawling disallowed by robots.txt for {url}")

        try:
            response = self.session.get(url, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip() if soup.title else ""
                return {"url": url, "title": title, "html": response.text}
        except Exception as e:
            logger.warning(f"Requests failed for {url}: {e}")
        
        try:
            browser = self._get_browser()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
            html = page.content()
            title = page.title()
            page.close()
            return {"url": url, "title": title, "html": html}
        except Exception as e:
            logger.error(f"Playwright failed for {url}: {e}")
            raise
    
    def parse_page_content(self, base_url: str, html: str) -> Dict[str, any]:
        """
        Extract content and same-domain links from HTML.
        """
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title else ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"].strip() if description_tag else ""
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        content = "\n".join(paragraphs[:settings.MAX_CONTENT_PARAGRAPHS])
        base_domain = urlparse(base_url).netloc
        links = set()
        
        for link in soup.find_all("a", href=True):
            href = urljoin(base_url, link["href"])
            if not is_excluded_url(href) and urlparse(href).netloc == base_domain:
                links.add(href)
        
        return {
            "title": title,
            "description": description,
            "content": content,
            "links": list(links)
        }
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and scheme."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and parsed.netloc
        except Exception:
            return False
       
def crawl_url_job(url_job_id: int) -> None:
    session = SessionLocal()
    job = session.get(URLJob, url_job_id)
    
    if not job:
        logger.error(f"URLJob {url_job_id} not found")
        session.close()
        return
    
    job.status = "in_progress"
    job.last_crawled = datetime.datetime.utcnow()
    session.commit()
    
    crawled_pages = []
    visited: Set[str] = set()
    queue = deque([(job.url, 0)])
    
    try:
        with WebCrawler() as crawler:
            ## CHANGED: Setup the robot parser before starting the crawl
            crawler.setup_robot_parser(job.url)
            
            while queue and len(crawled_pages) < settings.MAX_PAGES:
                current_url, depth = queue.popleft()
                
                if current_url in visited or depth > settings.MAX_DEPTH:
                    continue
                
                logger.info(f"Crawling ({len(crawled_pages)+1}/{settings.MAX_PAGES}): {current_url}")
                
                try:
                    page_data = crawler.fetch_page_content(current_url)
                    parsed_data = crawler.parse_page_content(current_url, page_data["html"])
                    parsed_data["url"] = current_url
                    parsed_data["title"] = page_data["title"] or parsed_data["title"]
                    
                    crawled_pages.append(parsed_data)
                    visited.add(current_url)
                    
                    if depth < settings.MAX_DEPTH:
                        for link in parsed_data["links"]:
                            if link not in visited:
                                queue.append((link, depth + 1))
                except Exception as e:
                    logger.error(f"Error crawling {current_url}: {e}")
                    continue
        
        if crawled_pages:
            llm_text = generate_llms_txt(crawled_pages, job.url)
            job.llm_text_content = llm_text
            job.content_hash = get_text_hash(llm_text)
            job.status = "completed"
            
            filename = f"llms_{job.id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(llm_text)
            logger.info(f"llms.txt written to {filename}")
        else:
            job.status = "error"
            job.error_stack = "No pages were successfully crawled"
    
    except Exception as e:
        logger.error(f"Fatal error in crawler: {e}")
        job.status = "error"
        job.error_stack = traceback.format_exc()
    
    finally:
        session.commit()
        session.close()