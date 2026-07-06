"""
Shared internal data structures and representations.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Article:
    """Structure representing a single scraped support article."""
    id: str
    title: str
    body_html: str
    url: str
    updated_at: str
    slug: str
    body_markdown: Optional[str] = None
    checksum: Optional[str] = None
