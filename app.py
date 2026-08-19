import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(title="ML Model Serving Platform")

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    "ml_inference_requests_total",
    "Total number of inference requests",
    ["model_name", "status"]
)

INFERENCE_LATENCY = Histogram(
    "ml_inference_duration_seconds",
    "Time spent processing inference request in seconds",
    ["model_name"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Mount Prometheus metrics endpoint (/metrics)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

class InferenceRequest(BaseModel):
    text: str

class InferenceResponse(BaseModel):
    sentiment: str
    confidence: float
    latency_ms: float

@app.get("/healthz")
def health_check():
    return {"status": "healthy"}

@app.post("/predict", response_model=InferenceResponse)
def predict(request: InferenceRequest):
    start_time = time.time()
    model_name = "sentiment_analyzer_v1"
    
    if not request.text.strip():
        REQUEST_COUNT.labels(model_name=model_name, status="400").inc()
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    try:
        # Dummy lightweight ML inference logic (e.g., sentiment scoring)
        # Real-world me yahan aapka PyTorch/Transformers pipeline call hoga
        time.sleep(0.05)  # Simulating compute overhead
        sentiment = "POSITIVE" if "good" in request.text.lower() else "NEUTRAL"
        confidence = 0.92
        
        duration = time.time() - start_time
        INFERENCE_LATENCY.labels(model_name=model_name).observe(duration)
        REQUEST_COUNT.labels(model_name=model_name, status="200").inc()
        
        return InferenceResponse(
            sentiment=sentiment,
            confidence=confidence,
            latency_ms=round(duration * 1000, 2)
        )
    except Exception as e:
        REQUEST_COUNT.labels(model_name=model_name, status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))