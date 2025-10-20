"""
Web crawler implementation for intelligent content extraction and monitoring.

This module implements a sophisticated web crawler system designed for content monitoring
and LLM text generation. The crawler features:

Key Components:
1. WebCrawler Class:
   - Context manager for resource management (browser, session cleanup)
   - Dual crawling strategy: requests library with Playwright fallback
   - Robots.txt compliance checking
   - HTTP caching support (ETag/Last-Modified headers)
   - Content validation (HTML type, size limits)

2. Smart Crawling Algorithm:
   - Breadth-first traversal with configurable depth limits
   - Page-level change detection using HTTP caching headers
   - Content deduplication and normalization
   - Intelligent content extraction (prioritizes main content containers)
   - Same-domain link discovery and filtering

3. Content Processing:
   - BeautifulSoup-based HTML parsing
   - Smart content extraction (articles, main containers)
   - Metadata extraction (title, description)
   - Content scoring based on crawl depth
   - Link normalization and filtering

4. Database Integration:
   - SQLAlchemy ORM for persistent storage
   - Page lifecycle management (grace period for stale pages)
   - Progress tracking and status updates
   - Conditional LLM text regeneration

5. Performance Optimizations:
   - HTTP HEAD requests for change detection
   - Cached link processing for unchanged pages
   - Randomized politeness delays (1-3 seconds)
   - Memory-efficient page pruning by score
   - Graceful error handling and fallbacks

The crawler is designed to be respectful of target websites while efficiently
extracting and monitoring content changes for downstream LLM processing.

"""
import logging
import traceback
import time
import json
import requests
import random
import datetime

from collections import deque
from typing import Dict, Set, Optional
from urllib.parse import urljoin, urlparse
from urllib import robotparser
from playwright.async_api import async_playwright, Browser
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from . import helper
from .database import SessionLocal
from .models import URLJob, CrawledPage
from .core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebCrawler:
    """Standardized web crawler instance to handle fallback"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': settings.USER_AGENT})
        self._browser: Optional[Browser] = None
        self._playwright = None
        self.robot_parser = robotparser.RobotFileParser()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, schedule the cleanup
                loop.create_task(self.cleanup())
            else:
                # If we're not in an async context, run it
                asyncio.run(self.cleanup())
        except RuntimeError:
            # Fallback if no event loop exists
            asyncio.run(self.cleanup())
        
    async def cleanup(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        self.session.close()

    def setup_robot_parser(self, root_url: str):
        """Fetches and parses the robots.txt file for the given domain."""
        robots_url = urljoin(root_url, "robots.txt")
        self.robot_parser.set_url(robots_url)
        try:
            self.robot_parser.read()
            logger.info(f"Successfully parsed robots.txt for {root_url}")
        except Exception as e:
            logger.warning(f"Could not read robots.txt for {root_url}: {e}")

    async def _get_browser(self) -> Browser:
        if not self._browser:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser
    
    def check_url_with_head(self, url: str, etag: Optional[str] = None, last_modified: Optional[str] = None) -> Dict[str, any]:
        """
        Perform HEAD request to check Content-Type, Content-Length, and caching headers.
        Returns dict with is_valid, status, content_type, etag, last_modified, and reason.
        """
        if not self.robot_parser.can_fetch(settings.USER_AGENT, url):
            return {"is_valid": False, "status": "FORBIDDEN", "reason": "Disallowed by robots.txt"}
        
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
        if last_modified:
            headers['If-Modified-Since'] = last_modified
        
        try:
            response = self.session.head(url, timeout=settings.REQUESTS_TIMEOUT, allow_redirects=True, headers=headers)
            
            # Check for 304 Not Modified
            if response.status_code == 304:
                return {
                    'is_valid': True,
                    'status': 'NOT_MODIFIED',
                    'reason': 'Page not modified (304)'
                }
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                # Check if it's HTML content
                if 'text/html' not in content_type:
                    return {
                        'is_valid': False,
                        'status': 'INVALID_TYPE',
                        'content_type': content_type,
                        'reason': f'Not HTML content: {content_type}'
                    }
                
                # Check content length, if it is more than 10MB, return false
                content_length = response.headers.get('content-length')
                if content_length:
                    try:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > 10:
                            return {
                                'is_valid': False,
                                'status': 'TOO_LARGE',
                                'reason': f'File too large: {size_mb:.1f}MB'
                            }
                    except ValueError:
                        pass
                
                return {
                    'is_valid': True,
                    'status': 'MODIFIED',
                    'content_type': content_type,
                    'etag': response.headers.get('ETag'),
                    'last_modified': response.headers.get('Last-Modified'),
                    'reason': None
                }
            
            return {
                'is_valid': False,
                'status': 'ERROR',
                'reason': f'HEAD request returned status {response.status_code}'
            }
            
        except Exception as e:
            logger.warning(f"HEAD request failed for {url}: {e}")
            # If HEAD fails, still try GET as fallback
            return {
                'is_valid': True,
                'status': 'HEAD_FAILED',
                'reason': f'HEAD failed, will try GET: {e}'
            }
    
    def _is_spa_shell(self, html: str, url: str) -> bool:
        """
        Detect if HTML is likely a JavaScript SPA shell with no rendered content.
        Indicators: Few links, minimal content, SPA framework markers.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Count actual content links (not just navigation)
        links = soup.find_all('a', href=True)
        valid_links = [
            link for link in links 
            if link.get('href') and not link.get('href').startswith('#')
            and not link.get('href').startswith('javascript:')
        ]
        
        # Check for common SPA framework indicators
        spa_indicators = [
            soup.find('div', id='root'),  # React
            soup.find('div', id='app'),   # Vue
            soup.find('div', id='__next'),  # Next.js
            soup.find('ng-app'),  # Angular
            soup.find('div', {'data-reactroot': True}),
            soup.find('div', {'data-react-root': True}),
        ]
        has_spa_marker = any(indicator for indicator in spa_indicators)
        
        # Check for minimal body content (mostly scripts and noscript)
        body = soup.find('body')
        if body:
            # Count non-script, non-style, non-noscript elements with actual text
            content_elements = [
                elem for elem in body.find_all(['p', 'div', 'article', 'section', 'main'])
                if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 20
            ]
            has_minimal_content = len(content_elements) < 3
        else:
            has_minimal_content = True
        
        # Verdict: It's likely an SPA shell if it has framework markers and few links/content
        is_spa = has_spa_marker and (len(valid_links) < 5 or has_minimal_content)
        
        if is_spa:
            logger.info(f"Detected SPA shell for {url} (links: {len(valid_links)}, spa_marker: {has_spa_marker}, minimal_content: {has_minimal_content})")
        
        return is_spa
    
    async def fetch_page_content(self, url: str) -> Dict[str, str]:
        """
        Fetch page content with requests first, fallback to Playwright.
        Automatically detects and handles JavaScript-heavy SPAs.
        Returns dict with url, title, html, etag, and last_modified.
        """
        if not helper.is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
            
        # if not self.robot_parser.can_fetch(settings.USER_AGENT, url):
        #     raise Exception(f"Crawling disallowed by robots.txt for {url}")

        should_fallback = False
        try:
            response = self.session.get(url, timeout=settings.REQUESTS_TIMEOUT)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                # Check if this is a JavaScript SPA shell
                if self._is_spa_shell(response.text, url):
                    logger.info(f"SPA detected for {url}, using Playwright for full rendering")
                    should_fallback = True
                else:
                    # Regular HTML page, use requests result
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.get_text(strip=True) if soup.title else ""
                    return {
                        "url": url,
                        "title": title,
                        "html": response.text,
                        "etag": response.headers.get('ETag'),
                        "last_modified": response.headers.get('Last-Modified')
                    }
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            logger.warning(f"Requests HTTP error for {url}: {e} (status: {status_code})")
            
            # Skip Playwright fallback for errors it can't help with
            if status_code in [403, 404, 500]:  # Forbidden, Not Found, Internal Server Error
                logger.info(f"Skipping Playwright fallback for HTTP {status_code} - Playwright won't help")
                raise  # Re-raise the original exception
            else:
                # For other HTTP errors, try Playwright fallback
                should_fallback = True
        except Exception as e:
            logger.warning(f"Requests failed for {url}: {e}")
            # For non-HTTP errors, try Playwright fallback
            should_fallback = True
        
        # Playwright fallback - for errors or detected SPAs
        if should_fallback:
            try:
                logger.info(f"Attempting Playwright fallback for {url}")
                browser = await self._get_browser()
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=settings.PLAYWRIGHT_TIMEOUT)
                html = await page.content()
                title = await page.title()
                await page.close()
                
                logger.info(f"Playwright fallback successful for {url}")
                return {
                    "url": url,
                    "title": title,
                    "html": html,
                    "etag": None,
                    "last_modified": None
                }
            except Exception as e:
                logger.error(f"Playwright fallback failed for {url}: {e}")
                raise
    
    def parse_page_content(self, base_url: str, html: str) -> Dict[str, any]:
        """
        Extract content and same-domain links from HTML.
        Smart extraction: prefer main content containers, fallback to individual elements.
        """
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.get_text(strip=True) if soup.title else ""
        description_tag = soup.find("meta", attrs={"name": "description"}) or \
                          soup.find("meta", attrs={"property": "og:description"})
        _desc_content = description_tag.get("content") if description_tag else ""
        description = _desc_content.strip() if isinstance(_desc_content, str) else ""
        
        content_parts = []
        
        # Try to find main content container first
        main_container = soup.find(['article', 'main']) or soup.find('div', class_=['content', 'main-content', 'article-content'])
        
        if main_container:
            # Extract from main container only
            for elem in main_container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
                text = elem.get_text(" ", strip=True)
                if text and len(text) > 10:  # Filter out very short snippets
                    content_parts.append(text)
        else:
            # Fallback: extract from entire page
            for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
                text = elem.get_text(" ", strip=True)
                if text and len(text) > 10:
                    content_parts.append(text)
        
        # Deduplicate while preserving order
        seen = set()
        unique_parts = []
        for part in content_parts:
            if part not in seen:
                seen.add(part)
                unique_parts.append(part)
        
        content = "\n".join(unique_parts[:settings.MAX_CONTENT_PARAGRAPHS])
        
        # Extract links (unchanged)
        base_domain = urlparse(base_url).netloc
        links = set()
        for link in soup.find_all("a", href=True):
            href = urljoin(base_url, link["href"])
            if not helper.is_excluded_url(href) and urlparse(href).netloc == base_domain:
                links.add(href)
        
        return {
            "title": title,
            "description": description,
            "content": content,
            "links": list(links)
        }
   
async def crawl_url_job(url_job_id: int) -> None:
    """
    Smart crawl with page-level change detection.
    Uses HTTP caching (ETag/Last-Modified) to avoid re-downloading unchanged pages.
    Keeps top MAX_PAGES pages by depth-based ranking.
    """
    session = SessionLocal()
    job = session.get(URLJob, url_job_id)
    
    if not job:
        logger.error(f"URLJob {url_job_id} not found")
        session.close()
        return
    
    job.status = "in_progress"
    job.progress_percentage = 5
    job.progress_message = "Starting crawler..."
    job.last_crawled = datetime.datetime.now(datetime.timezone.utc)
    session.commit()
    
    # Setup
    current_crawl_time = datetime.datetime.now(datetime.timezone.utc)
    
    # Load existing pages into dict for fast lookup
    existing_pages: Dict[str, CrawledPage] = {
        helper.normalize_url(p.url): p 
        for p in session.query(CrawledPage).filter_by(url_job_id=job.id).all()
    }
    
    # Capture initial state for comparison after pruning
    initial_page_states = {
        url: page.content_hash 
        for url, page in existing_pages.items()
    }
    
    seen_in_this_crawl: Set[str] = set()
    visited: Set[str] = set()
    normalized_root_url = helper.normalize_url(job.url)
    queue = deque([(normalized_root_url, 0)])
    
    pages_fetched = 0  # Counter for MAX_PAGES limit
    
    try:
        with WebCrawler() as crawler:
            crawler.setup_robot_parser(job.url)
            
            while queue and pages_fetched < settings.MAX_PAGES:
                current_url, depth = queue.popleft()
                normalized_url = helper.normalize_url(current_url)
                
                if normalized_url in visited or depth > settings.MAX_DEPTH:
                    continue
                
                visited.add(normalized_url)
                seen_in_this_crawl.add(normalized_url)
                
                page_record = existing_pages.get(normalized_url)
                
                # Check if page exists and is fresh
                if page_record:
                    head_check = crawler.check_url_with_head(
                        normalized_url,
                        page_record.etag,
                        page_record.last_modified
                    )
                    
                    if head_check['status'] == 'NOT_MODIFIED':
                        logger.info(f"Skipping {normalized_url}: Not Modified (304)")
                        page_record.last_seen = current_crawl_time
                        page_record.not_seen_count = 0  # Reset counter
                        
                        # Add cached links to queue
                        if depth < settings.MAX_DEPTH and page_record.links:
                            try:
                                cached_links = json.loads(page_record.links) if page_record.links else []
                                for link in cached_links:
                                    norm_link = helper.normalize_url(link)
                                    if norm_link not in visited:
                                        queue.append((norm_link, depth + 1))
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse cached links for {normalized_url}")
                        
                        continue 
                    
                    elif not head_check['is_valid']:
                        logger.warning(f"Skipping {normalized_url}: {head_check['reason']}")
                        continue
                
                # Fetch page (either new or modified)
                try:
                    logger.info(f"Fetching {normalized_url} (Depth: {depth}, Count: {pages_fetched+1}/{settings.MAX_PAGES})")
                    
                    # Update progress
                    job.progress_percentage = min(5 + int((pages_fetched / settings.MAX_PAGES) * 80), 85)
                    job.progress_message = "Crawling website..."
                    session.commit()
                    
                    page_data = await crawler.fetch_page_content(normalized_url)
                    parsed_data = crawler.parse_page_content(normalized_url, page_data["html"])
                    
                    # Calculate content hash and score
                    new_hash = helper.get_text_hash(parsed_data["content"])
                    new_score = helper.calculate_page_score(depth)
                    
                    if page_record:
                        # Update existing page
                        old_hash = page_record.content_hash  # Store old hash
                        logger.info(f"Updating {normalized_url}")
                        page_record.content_hash = new_hash
                        page_record.page_title = parsed_data["title"]
                        page_record.page_description = parsed_data["description"]
                        page_record.page_content = parsed_data["content"]
                        page_record.etag = page_data.get("etag")
                        page_record.last_modified = page_data.get("last_modified")
                        page_record.links = json.dumps(parsed_data.get("links", []))
                        page_record.depth = depth
                        page_record.page_score = new_score
                        page_record.last_seen = current_crawl_time
                        page_record.not_seen_count = 0
                        
                        # Log content changes
                        if old_hash != new_hash:
                            logger.info(f"Content hash changed for {normalized_url}")
                        else:
                            logger.info(f"Content unchanged for {normalized_url}")
                    else:
                        # Create new page
                        logger.info(f"Creating new page: {normalized_url}")
                        page_record = CrawledPage(
                            url_job_id=job.id,
                            url=normalized_url,
                            depth=depth,
                            content_hash=new_hash,
                            page_title=parsed_data["title"],
                            page_description=parsed_data["description"],
                            page_content=parsed_data["content"],
                            etag=page_data.get("etag"),
                            last_modified=page_data.get("last_modified"),
                            links=json.dumps(parsed_data.get("links", [])),
                            page_score=new_score,
                            last_seen=current_crawl_time,
                            not_seen_count=0
                        )
                        session.add(page_record)
                        existing_pages[normalized_url] = page_record
                    
                    pages_fetched += 1
                    
                    # Add links to queue
                    if depth < settings.MAX_DEPTH:
                        for link in parsed_data.get("links", []):
                            norm_link = helper.normalize_url(link)
                            if norm_link not in visited:
                                queue.append((norm_link, depth + 1))
                    
                    # Politeness delay with randomization
                    if pages_fetched < settings.MAX_PAGES:
                        delay = random.uniform(1, 3)  # Random delay between 1-3 seconds
                        logger.info(f"Waiting {delay:.2f} seconds...")
                        time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Error crawling {normalized_url}: {e}")
                    continue
        
        # Post-crawl cleanup
        logger.info("Crawl complete. Processing page lifecycle...")
        
        # Update not_seen_count for pages not found in this crawl
        for url, page in existing_pages.items():
            if url not in seen_in_this_crawl:
                page.not_seen_count += 1
                logger.info(f"Page {url} not seen (count: {page.not_seen_count})")
        
        session.commit()
        
        # Delete pages with not_seen_count >= GRACE_PERIOD_CRAWLS
        deleted_count = 0
        for url, page in list(existing_pages.items()):
            if page.not_seen_count >= settings.GRACE_PERIOD_CRAWLS:
                logger.info(f"Deleting {url}: Not seen for {page.not_seen_count} crawls")
                session.delete(page)
                del existing_pages[url]
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} pages due to grace period expiration")
            session.commit()
        
        # Keep only top MAX_PAGES by score
        all_pages = list(existing_pages.values())
        if len(all_pages) > settings.MAX_PAGES:
            logger.info(f"Pruning pages: {len(all_pages)} -> {settings.MAX_PAGES}")
            all_pages.sort(key=lambda p: p.page_score, reverse=True)
            pages_to_delete = all_pages[settings.MAX_PAGES:]
            
            for page in pages_to_delete:
                logger.info(f"Deleting low-priority page: {page.url} (score: {page.page_score})")
                session.delete(page)
            
            session.commit()
        
        # Update progress for llms.txt generation
        job.progress_percentage = 90
        job.progress_message = "Generating llms.txt..."
        session.commit()
        
        # Check if any pages changed and conditionally generate llms.txt
        final_pages = session.query(CrawledPage).filter_by(url_job_id=job.id).order_by(CrawledPage.page_score.desc()).all()
        
        if not final_pages:
            job.status = "error"
            job.error_stack = "No pages were successfully crawled"
        else:
            # Create final state snapshot
            final_page_states = {
                helper.normalize_url(page.url): page.content_hash 
                for page in final_pages
            }
            
            # Compare initial vs final state
            if job.last_monitored:  # Not first crawl
                pages_changed = (initial_page_states != final_page_states)
                
                # Detailed logging
                if pages_changed:
                    added = set(final_page_states.keys()) - set(initial_page_states.keys())
                    removed = set(initial_page_states.keys()) - set(final_page_states.keys())
                    modified = {
                        url for url in final_page_states 
                        if url in initial_page_states 
                        and final_page_states[url] != initial_page_states[url]
                    }
                    logger.info(f"State changed for {job.url}: {len(added)} added, {len(removed)} removed, {len(modified)} modified")
            else:
                pages_changed = True  # First crawl
            
            # Only regenerate llms.txt if state changed or this is the first crawl
            if pages_changed or not job.llm_text_content:
                logger.info(f"Regenerating llms.txt for {job.url}")
                llm_text = helper.generate_llms_txt(final_pages, job.url)
                job.llm_text_content = llm_text
                job.content_hash = helper.get_text_hash(llm_text)
                
                logger.info(f"LLM text generated and stored in database ({len(final_pages)} pages)")
            else:
                logger.info(f"No state changes detected for {job.url}, skipping llms.txt regeneration")
            
            job.status = "completed"
            job.progress_percentage = 100
            job.progress_message = "Complete"
    
    except Exception as e:
        logger.error(f"Fatal error in crawler: {e}")
        logger.error(traceback.format_exc())
        job.status = "error"
        job.progress_percentage = 0
        job.progress_message = "Error occurred"
        job.error_stack = traceback.format_exc()
    
    finally:
        session.commit()
        session.close()