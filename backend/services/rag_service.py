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
MAX_DISTANCE = 0.90


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
    "estou",
    "sentindo",
    "sentir",
    "tenho",
    "meu",
    "minha",
}


TOPIC_ALIASES = {
    "ansiedade": {
        "ansiedade",
        "ansioso",
        "ansiosa",
        "anxiety",
        "anxious",
        "worry",
        "worried",
        "fear",
        "panic",
    },
    "depressao": {
        "depressao",
        "depressivo",
        "depressiva",
        "depression",
        "depressive",
        "sadness",
        "sad",
    },
    "panico": {
        "panico",
        "panic",
        "ataque",
        "attack",
        "panic attack",
    },
    "suicidio": {
        "suicidio",
        "suicida",
        "suicide",
        "suicidal",
        "autolesao",
        "automutilacao",
        "self-harm",
        "self harm",
    },
    "estresse": {
        "estresse",
        "stress",
        "burnout",
        "esgotamento",
    },
    "insonia": {
        "insonia",
        "insomnia",
        "sono",
        "sleep",
        "sleeplessness",
    },
    "bipolaridade": {
        "bipolaridade",
        "bipolar",
        "mania",
        "maniaco",
        "manic",
    },
    "psicose": {
        "psicose",
        "psychosis",
        "psicotico",
        "psychotic",
        "alucinacao",
        "hallucination",
        "delirio",
        "delusion",
    },
}


GENERIC_TERMS = {
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
    "emocional",
    "emocionais",
}


def _empty_results() -> dict[str, list[list[Any]]]:
    return {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }


def _normalize_text(text: str) -> str:
    """
    Converte o texto para minúsculas e remove acentos.

    Exemplo:
    "Ansiedade" vira "ansiedade".
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
    Extrai palavras relevantes da pergunta.
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


def _expand_keywords(question: str) -> set[str]:
    """
    Expande palavras da pergunta com termos relacionados
    em português e inglês.
    """

    normalized_question = _normalize_text(question)

    keywords = _extract_keywords(question)

    expanded_keywords = set(keywords)

    for topic, aliases in TOPIC_ALIASES.items():
        normalized_topic = _normalize_text(topic)

        normalized_aliases = {
            _normalize_text(alias)
            for alias in aliases
        }

        topic_detected = (
            normalized_topic in normalized_question
            or any(
                alias in normalized_question
                for alias in normalized_aliases
            )
        )

        if topic_detected:
            expanded_keywords.add(normalized_topic)
            expanded_keywords.update(normalized_aliases)

    return expanded_keywords


def _get_specific_keywords(
    keywords: set[str],
) -> set[str]:
    """
    Remove termos muito genéricos e mantém palavras
    mais específicas do tema.
    """

    return {
        keyword
        for keyword in keywords
        if keyword not in GENERIC_TERMS
    }


def _count_keyword_matches(
    keywords: set[str],
    text: str,
) -> set[str]:
    """
    Retorna os termos encontrados em um texto.
    """

    normalized_text = _normalize_text(text)

    return {
        keyword
        for keyword in keywords
        if keyword in normalized_text
    }


def _calculate_topic_bonus(
    question: str,
    source: str,
    document: str,
) -> float:
    """
    Dá pontuação adicional quando o tema principal da pergunta
    aparece no nome do arquivo ou no conteúdo do trecho.
    """

    normalized_question = _normalize_text(question)
    normalized_source = _normalize_text(source)
    normalized_document = _normalize_text(document)

    bonus = 0.0

    for topic, aliases in TOPIC_ALIASES.items():
        normalized_topic = _normalize_text(topic)

        normalized_aliases = {
            _normalize_text(alias)
            for alias in aliases
        }

        topic_detected = (
            normalized_topic in normalized_question
            or any(
                alias in normalized_question
                for alias in normalized_aliases
            )
        )

        if not topic_detected:
            continue

        if (
            normalized_topic in normalized_source
            or any(
                alias in normalized_source
                for alias in normalized_aliases
            )
        ):
            bonus += 1.20

        if (
            normalized_topic in normalized_document
            or any(
                alias in normalized_document
                for alias in normalized_aliases
            )
        ):
            bonus += 0.40

    return bonus


async def search_documents(
    question: str,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Pesquisa documentos no ChromaDB e realiza reranking híbrido.

    A pontuação combina:
    - similaridade vetorial;
    - palavras-chave;
    - termos em português e inglês;
    - relevância do nome do arquivo;
    - relevância do tema no conteúdo.
    """

    clean_question = question.strip()

    if not clean_question:
        return _empty_results()

    total_documents = collection.count()

    if total_documents == 0:
        return _empty_results()

    expanded_keywords = _expand_keywords(
        clean_question
    )

    specific_keywords = _get_specific_keywords(
        expanded_keywords
    )

    embedding_terms = " ".join(
        sorted(expanded_keywords)
    )

    expanded_query = (
        f"{clean_question} {embedding_terms}"
    ).strip()

    question_embedding = await generate_embedding(
        expanded_query
    )

    search_limit = min(
        max(limit * 30, 100),
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

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    distances = results.get(
        "distances",
        [[]],
    )[0]

    ranked_results: list[dict[str, Any]] = []

    print("\n========== BUSCA RAG ==========")
    print(f"Pergunta original: {clean_question}")
    print(f"Consulta expandida: {expanded_query}")
    print(
        "Palavras-chave expandidas: "
        f"{sorted(expanded_keywords)}"
    )
    print(
        "Palavras-chave específicas: "
        f"{sorted(specific_keywords)}"
    )
    print(
        f"Quantidade de candidatos: {search_limit}"
    )
    print("================================\n")

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if not isinstance(document, str):
            continue

        if not isinstance(distance, (int, float)):
            continue

        numeric_distance = float(distance)

        if numeric_distance > MAX_DISTANCE:
            continue

        current_metadata = metadata or {}

        source = str(
            current_metadata.get(
                "source",
                "",
            )
        )

        document_matches = _count_keyword_matches(
            expanded_keywords,
            document,
        )

        source_matches = _count_keyword_matches(
            expanded_keywords,
            source,
        )

        specific_document_matches = (
            document_matches.intersection(
                specific_keywords
            )
        )

        specific_source_matches = (
            source_matches.intersection(
                specific_keywords
            )
        )

        semantic_score = 1.0 - numeric_distance

        content_keyword_bonus = (
            len(document_matches) * 0.10
        )

        specific_content_bonus = (
            len(specific_document_matches) * 0.20
        )

        source_keyword_bonus = (
            len(source_matches) * 0.50
        )

        specific_source_bonus = (
            len(specific_source_matches) * 0.70
        )

        topic_bonus = _calculate_topic_bonus(
            question=clean_question,
            source=source,
            document=document,
        )

        final_score = (
            semantic_score
            + content_keyword_bonus
            + specific_content_bonus
            + source_keyword_bonus
            + specific_source_bonus
            + topic_bonus
        )

        ranked_results.append(
            {
                "document": document,
                "metadata": current_metadata,
                "distance": numeric_distance,
                "score": final_score,
                "document_matches": document_matches,
                "source_matches": source_matches,
                "specific_document_matches": (
                    specific_document_matches
                ),
                "specific_source_matches": (
                    specific_source_matches
                ),
                "topic_bonus": topic_bonus,
            }
        )

    ranked_results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    topic_results = [
        result
        for result in ranked_results
        if (
            result["specific_document_matches"]
            or result["specific_source_matches"]
            or result["topic_bonus"] > 0
        )
    ]

    if topic_results:
        selected_results = topic_results[:limit]
    else:
        selected_results = ranked_results[:limit]

    print(
        "\n========== RESULTADOS SELECIONADOS ==========\n"
    )

    if not selected_results:
        print(
            "Nenhum trecho passou pelos filtros."
        )

    for position, result in enumerate(
        selected_results,
        start=1,
    ):
        metadata = result["metadata"]

        print(f"Resultado {position}")
        print(
            f"Fonte: {metadata.get('source')}"
        )
        print(
            f"Página: {metadata.get('page')}"
        )
        print(
            f"Trecho: {metadata.get('chunk')}"
        )
        print(
            f"Distância: {result['distance']:.3f}"
        )
        print(
            f"Score final: {result['score']:.3f}"
        )
        print(
            f"Bônus de tema: "
            f"{result['topic_bonus']:.3f}"
        )
        print(
            "Termos encontrados no conteúdo: "
            f"{sorted(result['document_matches'])}"
        )
        print(
            "Termos encontrados na fonte: "
            f"{sorted(result['source_matches'])}"
        )
        print(
            result["document"][:400]
        )
        print("-" * 70)

    return {
        "documents": [
            [
                result["document"]
                for result in selected_results
            ]
        ],
        "metadatas": [
            [
                result["metadata"]
                for result in selected_results
            ]
        ],
        "distances": [
            [
                result["distance"]
                for result in selected_results
            ]
        ],
    }