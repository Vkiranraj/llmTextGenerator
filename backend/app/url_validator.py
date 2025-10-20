"""
URL validation service for security and safety checks.
Provides basic validation to prevent malicious URLs from being processed.
"""

import re
import ipaddress
from urllib.parse import urlparse
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of URL validation."""
    is_valid: bool
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class URLValidator:
    """Simple but effective URL validator for security."""
    
    def __init__(self):
        """Initialize validator with security rules."""
        # Allowed URL schemes
        self.allowed_schemes = {'http', 'https'}
        
        # Maximum URL length
        self.max_url_length = 2048
        
        # Suspicious patterns to block
        self.suspicious_patterns = [
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'file://',
            r'ftp://',
            r'mailto:',
            r'tel:',
            r'\.\./',  # Path traversal
            r'%2e%2e%2f',  # Encoded path traversal
            r'%2e%2e%5c',  # Windows path traversal
        ]
        
        # Private/local IP ranges and hostnames
        self.private_hostnames = {
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '::1',
            '0:0:0:0:0:0:0:1'
        }
        
        # Private IP ranges
        self.private_networks = [
            ipaddress.IPv4Network('10.0.0.0/8'),
            ipaddress.IPv4Network('172.16.0.0/12'),
            ipaddress.IPv4Network('192.168.0.0/16'),
            ipaddress.IPv4Network('127.0.0.0/8'),
            ipaddress.IPv4Network('169.254.0.0/16'),  # Link-local
        ]
    
    def validate_url(self, url: str) -> ValidationResult:
        """
        Validate a URL for security and safety.
        
        Args:
            url: URL string to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        if not url or not isinstance(url, str):
            return ValidationResult(
                is_valid=False,
                error="URL cannot be empty or non-string"
            )
        
        # Check URL length
        if len(url) > self.max_url_length:
            return ValidationResult(
                is_valid=False,
                error=f"URL too long (max {self.max_url_length} characters)"
            )
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"Invalid URL format: {str(e)}"
            )
        
        # Check for suspicious patterns first (includes scheme checks)
        pattern_result = self._check_suspicious_patterns(url)
        if not pattern_result.is_valid:
            return pattern_result
        
        # Check scheme
        scheme_result = self._validate_scheme(parsed.scheme)
        if not scheme_result.is_valid:
            return scheme_result
        
        # Check domain/host
        domain_result = self._validate_domain(parsed.netloc)
        if not domain_result.is_valid:
            return domain_result
        
        # Check for private/local addresses
        private_result = self._check_private_addresses(parsed.netloc)
        if not private_result.is_valid:
            return private_result
        
        return ValidationResult(is_valid=True)
    
    def _validate_scheme(self, scheme: str) -> ValidationResult:
        """Validate URL scheme."""
        if not scheme:
            return ValidationResult(
                is_valid=False,
                error="URL must have a scheme (http:// or https://)"
            )
        
        if scheme.lower() not in self.allowed_schemes:
            return ValidationResult(
                is_valid=False,
                error=f"Only {', '.join(self.allowed_schemes)} schemes are allowed"
            )
        
        return ValidationResult(is_valid=True)
    
    def _check_suspicious_patterns(self, url: str) -> ValidationResult:
        """Check for suspicious patterns in URL."""
        url_lower = url.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    error=f"URL contains suspicious pattern: {pattern}"
                )
        
        return ValidationResult(is_valid=True)
    
    def _validate_domain(self, netloc: str) -> ValidationResult:
        """Validate domain/host part of URL."""
        if not netloc:
            return ValidationResult(
                is_valid=False,
                error="URL must have a valid domain"
            )
        
        # Remove port if present
        domain = netloc.split(':')[0]
        
        # Check if it's a valid domain format
        if not self._is_valid_domain_format(domain):
            return ValidationResult(
                is_valid=False,
                error="Invalid domain format"
            )
        
        return ValidationResult(is_valid=True)
    
    def _is_valid_domain_format(self, domain: str) -> bool:
        """Check if domain has valid format."""
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
            return False
        
        # Cannot start or end with dot or hyphen
        if domain.startswith('.') or domain.endswith('.') or domain.startswith('-') or domain.endswith('-'):
            return False
        
        # Must contain at least one dot for public domains (but allow localhost for testing)
        if '.' not in domain and domain.lower() not in ['localhost']:
            return False
        
        return True
    
    def _check_private_addresses(self, netloc: str) -> ValidationResult:
        """Check if URL points to private/local addresses."""
        if not netloc:
            return ValidationResult(is_valid=True)
        
        # Remove port if present
        host = netloc.split(':')[0]
        
        # Check against known private hostnames
        if host.lower() in self.private_hostnames:
            return ValidationResult(
                is_valid=False,
                error="Private/local addresses are not allowed"
            )
        
        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(host)
            
            # Check if it's a private IP
            for private_net in self.private_networks:
                if ip in private_net:
                    return ValidationResult(
                        is_valid=False,
                        error="Private IP addresses are not allowed"
                    )
        except ValueError:
            # Not an IP address, assume it's a domain name
            pass
        
        return ValidationResult(is_valid=True)


# Global validator instance
url_validator = URLValidator()
