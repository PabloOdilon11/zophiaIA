from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import AnalyzeRequest, AnalysisResult, DatasetStats
from backend.services.analyzer import analyze_report, get_stats

app = FastAPI(title="Zophia API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Zophia Lite FastAPI Backend Running"}

@app.post("/api/analyze", response_model=AnalysisResult)
def analyze(req: AnalyzeRequest):
    return analyze_report(req.text)

@app.get("/api/dataset/stats", response_model=DatasetStats)
def dataset_stats():
    return get_stats()
