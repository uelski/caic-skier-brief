from fastapi.testclient import TestClient
from server.app import app

c = TestClient(app)

def test_health_and_predict():
    assert c.get("/api/health").status_code == 200
    p = c.post("/api/predict-text", json={"summaryText":"Considerable danger with wind slab"})
    assert p.status_code == 200
    assert "levels" in p.json()