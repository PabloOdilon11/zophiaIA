import os
import re
import unicodedata
from typing import Any

import chromadb

from backend.services.embedding_service import generate_embedding


VECTOR_DB_PATH = os.getenv(
    "VECTOR_DB_PATH",
    "backend/vector_db",
)

COLLECTION_NAME = "zophia_documents"

# Quanto menor a distância, maior a semelhança.
MAX_DISTANCE = 0.55


client = chromadb.PersistentClient(
    path=VECTOR_DB_PATH
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


STOP_WORDS = {
    "quais",
    "qual",
    "como",
    "para",
    "uma",
    "umas",
    "uns",
    "dos",
    "das",
    "que",
    "são",
    "ser",
    "tem",
    "principais",
    "sobre",
    "pessoa",
    "pessoas",
    "pode",
    "podem",
    "deve",
    "isso",
    "esse",
    "essa",
    "estes",
    "estas",
}


def _empty_results() -> dict[str, list[list[Any]]]:
    return {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }


def _normalize_text(text: str) -> str:
    """
    Converte para minúsculas e remove acentos.
    Exemplo: ansiedade e Ansiedade passam a ser iguais.
    """

    normalized = unicodedata.normalize(
        "NFD",
        text.lower(),
    )

    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )


def _extract_keywords(question: str) -> set[str]:
    """
    Retira palavras pouco importantes da pergunta e mantém
    somente termos úteis para verificar a relevância.
    """

    normalized_question = _normalize_text(question)

    words = re.findall(
        r"\b[a-z]{4,}\b",
        normalized_question,
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def _has_keyword_match(
    question: str,
    document: str,
) -> bool:
    """
    Exige que os termos principais da pergunta apareçam
    no documento. Palavras genéricas, como 'sintomas',
    não são suficientes sozinhas.
    """

    normalized_question = _normalize_text(question)
    normalized_document = _normalize_text(document)

    generic_terms = {
        "sintoma",
        "sintomas",
        "sinal",
        "sinais",
        "causa",
        "causas",
        "tratamento",
        "tratamentos",
        "ajuda",
        "problema",
        "problemas",
        "transtorno",
        "transtornos",
        "mental",
        "saude",
    }

    keywords = _extract_keywords(normalized_question)

    specific_keywords = {
        keyword
        for keyword in keywords
        if keyword not in generic_terms
    }

    if specific_keywords:
        return any(
            keyword in normalized_document
            for keyword in specific_keywords
        )

    return any(
        keyword in normalized_document
        for keyword in keywords
    )

async def search_documents(
    question: str,
    limit: int = 3,
) -> dict[str, Any]:
    """
    Pesquisa documentos no ChromaDB e remove resultados
    muito distantes ou pouco relacionados.
    """

    clean_question = question.strip()

    if not clean_question:
        return _empty_results()

    total_documents = collection.count()

    if total_documents == 0:
        return _empty_results()

    question_embedding = await generate_embedding(
        clean_question
    )

    # Busca mais resultados do que será retornado, pois alguns
    # podem ser eliminados pelos filtros.
    search_limit = min(
        max(limit * 3, 6),
        total_documents,
    )

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=search_limit,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    filtered_documents: list[str] = []
    filtered_metadatas: list[dict[str, Any]] = []
    filtered_distances: list[float] = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if not isinstance(document, str):
            continue

        if not isinstance(distance, (int, float)):
            continue

        if distance > MAX_DISTANCE:
            continue

        if not _has_keyword_match(
            clean_question,
            document,
        ):
            continue

        filtered_documents.append(document)
        filtered_metadatas.append(metadata or {})
        filtered_distances.append(float(distance))

        if len(filtered_documents) >= limit:
            break

    return {
        "documents": [filtered_documents],
        "metadatas": [filtered_metadatas],
        "distances": [filtered_distances],
    }