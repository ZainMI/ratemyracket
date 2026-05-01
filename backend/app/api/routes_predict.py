from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.predictor_service import predict_matchup, get_matchup_bundle

router = APIRouter(prefix="/predict", tags=["predict"])


class PredictRequest(BaseModel):
    player1_key: str
    player2_key: str


@router.post("")
def predict(req: PredictRequest):
    try:
        return predict_matchup(req.player1_key, req.player2_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bundle")
def predict_bundle(req: PredictRequest):
    try:
        return get_matchup_bundle(req.player1_key, req.player2_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
