import re
import logging

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extract and clean content from web search results"""
    
    def extract_clean_content(self, content: str) -> str:
        """Clean and extract meaningful content"""
        if not content:
            return ''
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove common noise patterns
        content = self._remove_noise_patterns(content)
        
        # Limit content length
        if len(content) > 500:
            content = content[:500].rsplit(' ', 1)[0] + '...'
        
        return content
    
    def clean_title(self, title: str) -> str:
        """Clean search result title"""
        if not title:
            return ''
        
        # Remove common title suffixes
        title = re.sub(r'\s*[-|]\s*(YouTube|Google|Wikipedia|.*\.com).*$', '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def _remove_noise_patterns(self, content: str) -> str:
        """Remove common noise patterns from content"""
        noise_patterns = [
            r'Skip to main content',
            r'Cookie.*?accept',
            r'Sign up.*?newsletter',
            r'Subscribe.*?updates',
            r'Follow us on.*?social',
            r'\d+\s*comments?',
            r'Share.*?Facebook.*?Twitter',
            r'Advertisement',
            r'Sponsored.*?content'
        ]
        
        for pattern in noise_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content

content_extractor = ContentExtractor()