"""
SearchSummary model for search summaries.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SearchSummary(BaseModel):
    """Represents a search summary."""
    
    summary_text: str = Field(..., description="AI-generated summary of search results")
    fetched_at: Optional[datetime] = Field(None, description="Timestamp when the search was performed")
