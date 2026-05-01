from typing import Dict, Optional
from pydantic import BaseModel


class PredictRequest(BaseModel):
    player1_key: str
    player2_key: str


class SportPrediction(BaseModel):
    score_p1: int
    score_p2: int
    base_pred_diff: Optional[float] = None
    resid_pred_diff: Optional[float] = None
    pred_diff: float
    pred_total: float


class PredictionResponse(BaseModel):
    player1: str
    player2: str
    player1_key: Optional[str] = None
    player2_key: Optional[str] = None
    player1_name: Optional[str] = None
    player2_name: Optional[str] = None
    sports: Dict[str, SportPrediction]
    total_p1: int
    total_p2: int
    total_diff: int
    winner: str
