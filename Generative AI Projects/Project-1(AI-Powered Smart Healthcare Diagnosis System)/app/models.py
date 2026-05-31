from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import json

class NewsArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str = Field(unique=True)
    published_date: datetime = Field(default_factory=datetime.utcnow)
    source: str
    content: Optional[str] = None
    
    # AI Processed fields
    summary: Optional[str] = None
    sentiment: Optional[str] = None # Positive, Neutral, Negative
    tags: str = Field(default="[]") # Stored as JSON string
    
    # Vector store flag
    is_embedded: bool = Field(default=False)
    
    def get_tags(self) -> List[str]:
        return json.loads(self.tags)
    
    def set_tags(self, tags_list: List[str]):
        self.tags = json.dumps(tags_list)
