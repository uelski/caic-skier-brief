from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Avalanche Baseline API", version="0.1")

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/health")
def health(): return {"ok": True, "llm": False}
