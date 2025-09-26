from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .db import latest, samples
from .baseline import rule_based_predict
from .schemas import PredictTextIn

app = FastAPI(title="Avalanche Baseline API", version="0.1")

# Dev CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

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

@app.post("/api/predict-text")
def predict_text(inp: PredictTextIn):
    return {"mode": "rule_based", "levels": rule_based_predict(inp.summaryText)}
