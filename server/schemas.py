from typing import Dict, Literal, Optional
from pydantic import BaseModel

ElevBand = Literal["below_treeline", "treeline", "above_treeline"]

class Forecast(BaseModel):
    id: Optional[str] = None
    date: str
    datetime: Optional[int] = None
    summary: str
    levels: Dict[ElevBand, int]  # 1..5

class PredictTextIn(BaseModel):
    summaryText: str

class PredictOut(BaseModel):
    mode: Literal["baseline","trained","fallback"]
    levels: Dict[ElevBand, int]
