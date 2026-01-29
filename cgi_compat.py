"""
Compatibility shim for cgi module (removed in Python 3.14)
This allows snowflake-connector-python to work with Python 3.14
"""

import sys

# Create a minimal cgi module for compatibility
class cgi_module:
    """Minimal cgi module replacement"""
    @staticmethod
    def parse_header(value):
        """Parse HTTP header"""
        if ';' in value:
            main, params = value.split(';', 1)
            return main.strip(), {}
        return value.strip(), {}
    
    @staticmethod
    def parse_multipart(fp, pdict):
        """Placeholder for multipart parsing"""
        return {}

# Inject into sys.modules before snowflake connector imports
sys.modules['cgi'] = cgi_module()
