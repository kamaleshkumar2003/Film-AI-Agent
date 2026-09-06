from typing import List
from pydantic import BaseModel

class PageContent(BaseModel):
    page_number: int
    text: str
    char_start: int
    char_end: int

class ExtractedDocument(BaseModel):
    full_text: str
    pages: List[PageContent]
    page_count: int
