# backend/main_simple.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NOWEX Simple API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "NOWEX Simple API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "NOWEX Simple API"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8002, reload=True)