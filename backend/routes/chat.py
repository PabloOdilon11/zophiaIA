from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.llm_service import generate_response


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=3000,
    )

    conversation_id: str | None = None


@router.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="A mensagem não pode estar vazia.",
        )

    try:
        result = await generate_response(
            question=message,
            conversation_id=request.conversation_id,
        )

        return {
            "response": result["response"],
            "conversation_id": result["conversation_id"],
            "model": "gemma3:4b",
        }

    except Exception as error:
        print(f"Erro na rota de chat: {error}")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível gerar a resposta.",
        ) from error