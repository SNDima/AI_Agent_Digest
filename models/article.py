from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime

class Article(BaseModel):
    guid: str
    source: str
    title: str
    link: HttpUrl
    summary: Optional[str] = None
    author: Optional[str] = None
    categories: List[str] = []
    published_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    posted: bool = False
