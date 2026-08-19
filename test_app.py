from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_prediction_positive():
    response = client.post("/predict", json={"text": "This model is good and fast"})
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "POSITIVE"
    assert data["confidence"] > 0
    assert "latency_ms" in data

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ml_inference_requests_total" in response.text