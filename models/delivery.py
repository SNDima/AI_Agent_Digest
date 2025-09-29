"""
Delivery model for delivery records.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Delivery(BaseModel):
    """Represents a delivery record of content to a delivery channel."""
    
    delivered_at: Optional[datetime] = Field(None, description="Timestamp when the content was delivered")
    content: str = Field(..., description="Content that was delivered")
    origin_message_id: Optional[str] = Field(None, description="ID of the original message if applicable")
