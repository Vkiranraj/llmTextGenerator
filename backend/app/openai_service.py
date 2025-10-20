"""
OpenAI service for Generative Engine Optimization (GEO).

This service provides AI-powered categorization and summary generation
for enhanced llms.txt content that's optimized for LLM consumption.
"""

import os
import logging
from typing import Dict, List, Optional
from openai import OpenAI
from .core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API integration with GEO optimization."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.client = None
            logger.warning("OpenAI API key not found. AI features will be disabled.")
        else:
            try:
                # Initialize OpenAI client with the API key
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    
    def analyze_page_content(self, title: str, description: str, content: str) -> Dict[str, str]:
        """
        Analyze page content and return both categorization and -optimized summary.
        
        Args:
            title: Page title
            description: Page description/meta description
            content: Main page content
            
        Returns:
            Dict with 'category' and 'summary' keys
        """
        if not self.client:
            return {
                "category": "Other",
                "summary": f"Content from {title or 'this page'}"
            }
        
        try:
            # Prepare content for analysis
            page_info = f"Title: {title}\nDescription: {description}\nContent: {content[:2000]}"
            
            prompt = f"""
            Analyze this webpage content and provide:
            1. A single-word category (e.g., "Technology", "Business", "Education", "Documentation", "Tutorial", "News", "Product", "Service")
            2. A concise, AI-optimized summary (2-3 sentences) that would be useful for an LLM to understand the page's purpose and value
            
            Webpage content:
            {page_info}
            
            Respond in this exact format:
            CATEGORY: [single word]
            SUMMARY: [2-3 sentence summary optimized for LLM understanding]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing web content and creating summaries optimized for AI/LLM consumption."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse response
            lines = result_text.split('\n')
            category = "Other"
            summary = "No summary available"
            
            for line in lines:
                if line.startswith("CATEGORY:"):
                    category = line.replace("CATEGORY:", "").strip()
                elif line.startswith("SUMMARY:"):
                    summary = line.replace("SUMMARY:", "").strip()
            
            return {
                "category": category,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return {
                "category": "Other",
                "summary": f"Content from {title or 'this page'}"
            }
    
    def categorize_page(self, title: str, description: str, content: str) -> str:
        """
        Categorize a page using AI analysis.
        
        Args:
            title: Page title
            description: Page description
            content: Page content
            
        Returns:
            Category string
        """
        analysis = self.analyze_page_content(title, description, content)
        return analysis["category"]
    
    def generate_geo_summary(self, title: str, description: str, content: str) -> str:
        """
        Generate LLM-optimized summary for LLM consumption.
        
        Args:
            title: Page title
            description: Page description
            content: Page content
            
        Returns:
            AI-optimized summary string
        """
        analysis = self.analyze_page_content(title, description, content)
        return analysis["summary"]
    
    def batch_analyze_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Analyze multiple pages in a single API call for efficiency.
        
        Args:
            pages: List of page dictionaries with 'title', 'description', 'content'
            
        Returns:
            List of enhanced page dictionaries with 'ai_category' and 'ai_summary'
        """
        if not self.client:
            return [
                {"ai_category": "Other", "ai_summary": "No summary available"}
                for _ in pages
            ]
        
        try:
            # Prepare batch content
            batch_content = ""
            for i, page in enumerate(pages):
                batch_content += f"Page {i+1}:\n"
                batch_content += f"Title: {page.get('title', '')}\n"
                batch_content += f"Description: {page.get('description', '')}\n"
                batch_content += f"Content: {page.get('content', '')[:1000]}\n\n"
            
            prompt = f"""
            Analyze these webpages and for each page provide:
            1. A single-word category
            2. A concise, AI-optimized summary (2-3 sentences) - Avoid ambiguous terms or unexplained jargon. Use concise, clear language.

            
            Pages to analyze:
            {batch_content}
            
            Respond in this exact format for each page:
            Page 1:
            CATEGORY: [single word]
            SUMMARY: [2-3 sentence summary]
            
            Page 2:
            CATEGORY: [single word]
            SUMMARY: [2-3 sentence summary]
            
            [continue for all pages]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing web content and creating summaries optimized for AI/LLM consumption."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens * 2,  # More tokens for batch processing
                temperature=self.temperature
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse batch response
            enhanced_pages = []
            current_page = None
            
            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith("Page "):
                    if current_page is not None:
                        enhanced_pages.append(current_page)
                    current_page = {"ai_category": "Other", "ai_summary": "No summary available"}
                elif line.startswith("CATEGORY:"):
                    if current_page is not None:
                        current_page["ai_category"] = line.replace("CATEGORY:", "").strip()
                elif line.startswith("SUMMARY:"):
                    if current_page is not None:
                        current_page["ai_summary"] = line.replace("SUMMARY:", "").strip()
            
            if current_page is not None:
                enhanced_pages.append(current_page)
            
            # Ensure we have results for all pages
            while len(enhanced_pages) < len(pages):
                enhanced_pages.append({
                    "ai_category": "Other",
                    "ai_summary": "No summary available"
                })
            
            return enhanced_pages[:len(pages)]  # Trim to exact count
            
        except Exception as e:
            logger.error(f"OpenAI batch analysis failed: {e}")
            # Return default values for all pages
            return [
                {"ai_category": "Other", "ai_summary": "No summary available"}
                for _ in pages
            ]

# Global instance
openai_service = OpenAIService()
