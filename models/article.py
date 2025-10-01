"""
Article model for RSS feed articles.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class Article(BaseModel):
    """Represents an article from an RSS feed or news source."""
    
    guid: str = Field(..., description="Unique identifier for the article")
    source: str = Field(..., description="Source website or feed name")
    title: str = Field(..., description="Title of the article")
    link: HttpUrl = Field(..., description="URL link to the full article")
    summary: Optional[str] = Field(None, description="Article summary or excerpt")
    author: Optional[str] = Field(None, description="Author of the article")
    categories: List[str] = Field(default_factory=list, description="List of article categories or tags")
    published_at: Optional[datetime] = Field(None, description="Publication date and time")
    fetched_at: Optional[datetime] = Field(None, description="Date and time when article was fetched")
    posted: bool = Field(False, description="Whether the article has been posted to delivery channel")
    relevance_score: Optional[int] = Field(None, description="Relevance score from 1-100 for AI agent content")
    relevance_prescore: Optional[int] = Field(None, description="Relevance prescore from a lighter LLM")
    reasoning: Optional[str] = Field(None, description="LLM reasoning for the relevance score")
