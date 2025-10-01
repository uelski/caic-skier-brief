from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .db import latest, samples
from .baseline import rule_based_predict
from .schemas import PredictTextIn
from typing import Literal, Dict, Any

# import predictors
from ml.predictors.tfidf_mlp import TfidfMLPPredictor

app = FastAPI(title="Avalanche Baseline API", version="0.1")

# Dev CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

ModelName = Literal["tfidf_mlp", "rule_based"] 

class PredictTextIn(BaseModel):
    summaryText: str = Field(...,min_length=1, description="The summary text to predict")
    model: ModelName = Field(default="tfidf_mlp", description="The model to use")

# Optional: type the response if you like
class PredictOut(BaseModel):
    below_treeline: int
    treeline: int
    above_treeline: int
    scores: Dict[str, list[float]] | None
    model_id: str

# ---- Predictor registry ----
_predictors: Dict[str, Any] = {}

@app.on_event("startup")
def startup():
    # Load once at startup (fast and thread-safe for inference)
    _predictors["tfidf_mlp"] = TfidfMLPPredictor()
    # _predictors["bilstm"]   = BiLSTMPredictor(...)     # when ready
    # _predictors["transformer"] = TransformerPred(...)  # when ready
    # rule_based is a function, not a class; we’ll route to it inline

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/health")
def health(): return {"ok": True, "llm": False}

@app.get("/api/latest")
def get_latest():
    f = latest()
    if not f:
        raise HTTPException(404, "no_data")
    return f

@app.get("/api/samples")
def get_samples(limit: int = Query(default=10, ge=1, le=100)):
    return {"forecasts": samples(limit)}

@app.post("/api/predict-levels")
def predict_levels(body: PredictTextIn) -> PredictOut:
    model_name = body.model

    if model_name == "rule_based":
        # Assuming your baseline returns the same shape
        # e.g., {"below_treeline": int, "treeline": int, "above_treeline": int, "scores": {...}, "model_id": "rule_based"}
        baseline_pred = rule_based_predict(body.summaryText)
        return PredictOut(**baseline_pred,scores=None, model_id="rule_based")

    predictor = _predictors.get(model_name)
    if predictor is None:
        raise HTTPException(status_code=400, detail=f"Unknown model '{model_name}'")

    # TF-IDF MLP (or other) predictor
    return predictor.predict_one(body.summaryText)
