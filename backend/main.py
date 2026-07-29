from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.routes.chat import router as chat_router
from backend.services.analyzer import (
    analyze_report,
    get_stats,
)


app = FastAPI(
    title="Zophia Lite API",
    description="Backend da assistente educativa Zophia.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


@app.get("/")
def read_root():
    return {
        "message": "Zophia Lite FastAPI Backend Running",
        "status": "online",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    clean_text = request.text.strip()

    if not clean_text:
        raise HTTPException(
            status_code=400,
            detail="O texto não pode estar vazio.",
        )

    try:
        return analyze_report(clean_text)

    except Exception as error:
        print(f"Erro durante a análise: {error}")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível analisar o texto.",
        ) from error


@app.get("/api/dataset/stats")
def dataset_stats():
    try:
        return get_stats()

    except Exception as error:
        print(f"Erro ao obter estatísticas: {error}")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível obter as estatísticas.",
        ) from error