from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Step0Input(BaseModel):
    dream: str


class SymbolMeaning(BaseModel):
    symbol: str
    meaning: str


# data structure for incoming dream-related input using Pydantic, which helps with validation and type safety.
class Step1Input(BaseModel):
    title: str
    dream: str
    symbols: List[SymbolMeaning]
    emotion: str
    context: Optional[str] = None


class Step2Input(BaseModel):
    resonated: str
    disagreed: str


class Step3Input(BaseModel):
    goal: str


class DreamInput(BaseModel):
    user_id: str
    dream_id: str
    step: int
    input_data: Dict[str, Any]  # initial raw input


# how to make an optional field
# context: Optional[str] = None  # Optional field
