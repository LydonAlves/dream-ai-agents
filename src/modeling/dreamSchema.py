from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Symbol(BaseModel):
    symbol: str
    meaning: Optional[str] = ""


class Dream(BaseModel):
    user_id: str
    dream_id: str
    title: str
    dream_text: str
    symbols: List[Symbol]
    emotion: str
    context: str
    date: int
    finalInterpretation: str
    created_at: datetime = Field(default=datetime.utcnow)
