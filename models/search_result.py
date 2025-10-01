"""
SearchResult model for individual search results.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class SearchResult(BaseModel):
    """Represents a single search result from a web search."""
    
    title: str = Field(..., description="Title of the search result")
    snippet: str = Field(..., description="Brief description or snippet of the content")
    source: str = Field(..., description="Source website or domain name (e.g., 'techcrunch.com')")
    published_date: str = Field(..., description="Published date")
    link: HttpUrl = Field(..., description="URL link to the full article")
    fetched_at: Optional[datetime] = Field(None, description="Date and time when search result was fetched")
