"""
SubScout — Subdomain discovery & port verification

This package provides:
- Passive subdomain enumeration from multiple sources
- Alive checks (ping / TCP / top ports)
- Async scanning & reporting
- Export to JSON, CSV, HTML
"""

__version__ = "0.1.0"

from .subscout import app
from .sources import gather_subdomains
from .scanner import verify_subdomains
from .utils import normalize_subdomain, TOP_100_PORTS
