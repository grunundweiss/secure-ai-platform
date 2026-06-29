# model_platform/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from inference_engine import LocalInferenceEngine

# Initialize the FastAPI platform application
app = FastAPI(
    title="Secure Local AI Platform API",
    description="Production-grade local inference serving layer for financial compliance logs.",
    version="1.0.0"
)

# Instantiate and pre-load the engine skeleton
engine = LocalInferenceEngine()
engine.initialize_platform(mock_mode=True)  # Using mock execution safety mode

# Define strict input schema for API requests
class InferenceRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=1000)
    max_tokens: int = Field(default=50, ge=10, le=200)

@app.get("/health", status_code=200)
async def health_check():
    """Liveness/Readiness probe endpoint for platform orchestration tools."""
    if engine is not None:
        return {"status": "healthy", "device": engine.device, "model": engine.model_id}
    raise HTTPException(status_code=503, detail="AI Engine uninitialized")

@app.post("/predict")
async def run_inference(payload: InferenceRequest):
    """Executes local language model token generation synchronously over the prompt input."""
    try:
        response_text = engine.generate_inference(
            prompt=payload.prompt,
            max_tokens=payload.max_tokens
        )
        return {
            "status": "success",
            "prompt": payload.prompt,
            "generated_text": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution engine failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Execute local diagnostic server layer
    uvicorn.run(app, host="127.0.0.1", port=8000)
