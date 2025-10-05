from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .db import latest, samples
from .baseline import rule_based_predict
from .schemas import PredictTextIn
from typing import Literal, Dict, Any
from contextlib import asynccontextmanager
from pathlib import Path
import os

load_dotenv()

# import predictors
from ml.predictors.tfidf_mlp import TfidfMLPPredictor

# ---------- minimal GCS helper ----------
def gcs_download_prefix(bucket: str, prefix: str, dest_root: Path) -> Path:
    # Only imported when needed, keeps local dev light
    from google.cloud import storage
    client = storage.Client()  # uses Cloud Run service account in prod
    dest = dest_root / prefix
    dest.mkdir(parents=True, exist_ok=True)
    for blob in client.list_blobs(bucket, prefix=prefix):
        if blob.name.endswith("/"):
            continue
        rel = blob.name[len(prefix):].lstrip("/")
        local_path = dest / rel
        local_path.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(local_path))
    return dest

# ---------- config & state ----------
ART_ROOT = Path("/app/artifacts")  # where we cache downloads in the container
PREDICTORS: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) Read env vars
    bucket = os.getenv("ARTIFACTS_BUCKET", "caic-ml-artifacts-prod")
    tfidf_prefix = os.getenv("TFIDF_PREFIX", "tfidf_mlp/v1")
    local_root = os.getenv("ARTIFACTS_LOCAL_DIR")  # set in local dev only

    # 2) Resolve artifact directory (local vs GCS)
    if local_root:
        # Local dev: no cloud download. Use your repo’s files directly.
        tfidf_path = Path(local_root) / tfidf_prefix
    else:
        # Prod (or when you want): download from GCS into /app/artifacts
        tfidf_path = gcs_download_prefix(bucket, tfidf_prefix, ART_ROOT)
    print(f"tfidf_path: {tfidf_path}")
    # 3) Instantiate predictors (pass the resolved folder)
    PREDICTORS["tfidf_mlp"] = TfidfMLPPredictor(artifacts_dir=str(tfidf_path))

    yield  # ---- app runs ----


app = FastAPI(title="Avalanche Baseline API", version="0.1", lifespan=lifespan)

# Dev CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

models = ["tfidf_mlp", "rule_based"]
ModelName = Literal[*models] 

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

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/health")
def health(): 
    return {
        "ok": True,
        "models": list(PREDICTORS.keys()) + ["rule_based"],
        "using_local": bool(os.getenv("ARTIFACTS_LOCAL_DIR")),
        "tfidf_prefix": os.getenv("TFIDF_PREFIX", "tfidf_mlp/v1"),
    }

@app.get("/api/latest")
def get_latest():
    f = latest()
    if not f:
        raise HTTPException(404, "no_data")
    return f

@app.get("/api/samples")
def get_samples(limit: int = Query(default=10, ge=1, le=100)):
    return {"forecasts": samples(limit)}

@app.get("/api/models")
def get_models():
    return {"models": models}

@app.post("/api/predict-levels")
def predict_levels(body: PredictTextIn) -> PredictOut:
    model_name = body.model

    if model_name == "rule_based":
        # Assuming your baseline returns the same shape
        # e.g., {"below_treeline": int, "treeline": int, "above_treeline": int, "scores": {...}, "model_id": "rule_based"}
        baseline_pred = rule_based_predict(body.summaryText)
        return PredictOut(**baseline_pred,scores=None, model_id="rule_based")

    predictor = PREDICTORS.get(model_name)
    if predictor is None:
        raise HTTPException(status_code=400, detail=f"Unknown model '{model_name}'")

    # TF-IDF MLP (or other) predictor
    return predictor.predict_one(body.summaryText)
