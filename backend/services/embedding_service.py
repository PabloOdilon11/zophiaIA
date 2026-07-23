import os
from typing import List

import httpx


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text",
)


class EmbeddingServiceError(Exception):
    """Erro ao gerar embeddings usando o Ollama."""


async def generate_embedding(text: str) -> List[float]:
    """
    Transforma um texto em uma lista de números.

    Essa lista representa semanticamente o conteúdo do texto
    e será usada pelo banco vetorial para comparar perguntas
    com trechos dos documentos.
    """

    clean_text = text.strip()

    if not clean_text:
        raise ValueError(
            "O texto para geração do embedding não pode estar vazio."
        )

    url = f"{OLLAMA_BASE_URL}/api/embeddings"

    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": clean_text,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

    except httpx.ConnectError as error:
        raise EmbeddingServiceError(
            "Não foi possível conectar ao Ollama. "
            "Verifique se ele está aberto."
        ) from error

    except httpx.TimeoutException as error:
        raise EmbeddingServiceError(
            "O Ollama demorou muito para gerar o embedding."
        ) from error

    except httpx.HTTPStatusError as error:
        raise EmbeddingServiceError(
            f"O Ollama retornou o erro HTTP "
            f"{error.response.status_code}."
        ) from error

    data = response.json()

    embedding = data.get("embedding")

    if not embedding:
        raise EmbeddingServiceError(
            "O Ollama não retornou um embedding válido."
        )

    return embedding