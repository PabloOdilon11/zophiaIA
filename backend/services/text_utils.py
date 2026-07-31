"""Funções utilitárias para normalização e comparação de texto."""

import re
import unicodedata

def _normalize_message(message: str) -> str:
    """
    Converte a mensagem para minúsculas, remove acentos,
    pontuação desnecessária e espaços duplicados.
    """

    normalized = unicodedata.normalize(
        "NFD",
        message.lower(),
    )

    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    normalized = re.sub(
        r"[^\w\s]",
        " ",
        normalized,
    )

    return " ".join(normalized.split())

def _contains_term(
    normalized_message: str,
    term: str,
) -> bool:
    """
    Verifica a presença de um termo completo na mensagem,
    evitando correspondências acidentais dentro de palavras.
    """

    normalized_term = _normalize_message(term)

    pattern = (
        r"(?<!\w)"
        + re.escape(normalized_term)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            normalized_message,
        )
    )

