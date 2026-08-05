import os
import re
import unicodedata
from typing import Any

import pandas as pd


DATASET_PATH = os.getenv(
    "DATASET_PATH",
    "datasets/mental_health_social_media_posts.csv",
)


ANXIETY_TERMS = {
    "ansiedade",
    "ansioso",
    "ansiosa",
    "nervoso",
    "nervosa",
    "preocupado",
    "preocupada",
    "preocupacao",
    "preocupação",
    "panico",
    "pânico",
    "medo",
    "agitado",
    "agitada",
    "inquieto",
    "inquieta",
    "palpitacao",
    "palpitação",
}

DEPRESSION_TERMS = {
    "depressao",
    "depressão",
    "deprimido",
    "deprimida",
    "triste",
    "tristeza",
    "desanimado",
    "desanimada",
    "vazio",
    "vazia",
    "sem energia",
    "sem vontade",
    "isolado",
    "isolada",
    "sozinho",
    "sozinha",
}

RISK_TERMS = {
    "quero morrer",
    "vou me matar",
    "me matar",
    "suicidio",
    "suicídio",
    "suicida",
    "tirar minha vida",
    "acabar com minha vida",
    "nao quero viver",
    "não quero viver",
    "seria melhor morrer",
    "queria desaparecer",
}

POSITIVE_TERMS = {
    "feliz",
    "bem",
    "otimo",
    "ótimo",
    "melhor",
    "animado",
    "animada",
    "tranquilo",
    "tranquila",
    "esperancoso",
    "esperançoso",
    "esperancosa",
    "esperançosa",
}


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize(
        "NFD",
        str(text).lower(),
    )

    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()


def _find_terms(
    text: str,
    terms: set[str],
) -> list[str]:
    normalized_text = _normalize_text(text)

    found_terms = []

    for term in terms:
        normalized_term = _normalize_text(term)

        if normalized_term in normalized_text:
            found_terms.append(term)

    return sorted(set(found_terms))


def detect_risk(text: str) -> list[str]:
    return _find_terms(
        text,
        RISK_TERMS,
    )


def detect_anxiety(text: str) -> list[str]:
    return _find_terms(
        text,
        ANXIETY_TERMS,
    )


def detect_depression(text: str) -> list[str]:
    return _find_terms(
        text,
        DEPRESSION_TERMS,
    )


def detect_positive(text: str) -> list[str]:
    return _find_terms(
        text,
        POSITIVE_TERMS,
    )


def classify_report(text: str) -> str:
    if detect_risk(text):
        return "risk"

    anxiety_signs = detect_anxiety(text)
    depression_signs = detect_depression(text)

    if anxiety_signs and depression_signs:
        return "mixed_distress"

    if anxiety_signs:
        return "anxiety"

    if depression_signs:
        return "depression"

    if detect_positive(text):
        return "positive"

    return "neutral"


def analyze_report(text: str) -> dict[str, Any]:
    clean_text = str(text).strip()

    if not clean_text:
        raise ValueError(
            "O texto para análise não pode estar vazio."
        )

    classification = classify_report(clean_text)

    anxiety_signs = detect_anxiety(clean_text)
    depression_signs = detect_depression(clean_text)
    risk_signs = detect_risk(clean_text)
    positive_signs = detect_positive(clean_text)

    observed_signs = sorted(
        set(
            anxiety_signs
            + depression_signs
            + risk_signs
            + positive_signs
        )
    )

    if classification == "risk":
        summary = (
            "Foram identificadas expressões que podem indicar "
            "risco ou sofrimento emocional intenso."
        )

        educational_information = (
            "Uma análise automática não consegue determinar com segurança "
            "a situação da pessoa. Expressões relacionadas à morte ou à "
            "autolesão precisam ser tratadas com atenção imediata."
        )

        recommendations = [
            "Procure imediatamente uma pessoa de confiança.",
            "Não permaneça sozinho enquanto estiver em risco.",
            "Busque um serviço de emergência ou atendimento profissional.",
        ]

        when_to_seek_help = (
            "Procure atendimento de emergência imediatamente caso exista "
            "intenção, planejamento ou risco de se machucar."
        )

    elif classification == "anxiety":
        summary = (
            "O texto contém palavras associadas a preocupação, "
            "medo ou ansiedade."
        )

        educational_information = (
            "Esses termos podem aparecer em diferentes situações e não são "
            "suficientes para indicar um diagnóstico."
        )

        recommendations = [
            "Observe há quanto tempo esses sentimentos estão acontecendo.",
            "Converse com uma pessoa de confiança.",
            "Considere procurar um profissional de saúde mental.",
        ]

        when_to_seek_help = (
            "Procure ajuda profissional quando o sofrimento for frequente, "
            "intenso ou estiver prejudicando sua rotina."
        )

    elif classification == "depression":
        summary = (
            "O texto contém palavras relacionadas a tristeza, "
            "desânimo ou isolamento."
        )

        educational_information = (
            "A presença dessas palavras não confirma um transtorno. "
            "Uma avaliação adequada deve ser feita por um profissional."
        )

        recommendations = [
            "Converse com alguém de confiança sobre como você está se sentindo.",
            "Evite enfrentar o sofrimento completamente sozinho.",
            "Considere buscar acompanhamento psicológico ou médico.",
        ]

        when_to_seek_help = (
            "Procure ajuda quando os sentimentos persistirem, se agravarem "
            "ou interferirem nas atividades diárias."
        )

    elif classification == "mixed_distress":
        summary = (
            "O texto contém sinais relacionados tanto à ansiedade "
            "quanto à tristeza ou ao desânimo."
        )

        educational_information = (
            "Os sinais encontrados são apenas indicadores textuais e não "
            "representam um diagnóstico clínico."
        )

        recommendations = [
            "Registre quando e em quais situações esses sentimentos aparecem.",
            "Converse com alguém de confiança.",
            "Procure avaliação de um profissional de saúde mental.",
        ]

        when_to_seek_help = (
            "Busque ajuda profissional se os sentimentos estiverem causando "
            "sofrimento intenso ou prejudicando sua rotina."
        )

    elif classification == "positive":
        summary = (
            "O texto contém expressões associadas a uma percepção positiva."
        )

        educational_information = (
            "Essa identificação considera apenas palavras presentes no texto "
            "e não determina o estado emocional completo da pessoa."
        )

        recommendations = [
            "Continue observando e cuidando do seu bem-estar.",
            "Mantenha contato com pessoas que ofereçam apoio.",
        ]

        when_to_seek_help = (
            "Mesmo em momentos positivos, procure ajuda caso exista sofrimento "
            "emocional que não tenha sido mencionado no texto."
        )

    else:
        summary = (
            "Não foram encontrados sinais textuais suficientes para "
            "classificar a mensagem."
        )

        educational_information = (
            "A ausência de palavras específicas não significa ausência de "
            "sofrimento. Esta ferramenta realiza apenas uma análise educativa."
        )

        recommendations = [
            "Descreva com mais detalhes o que está sentindo, caso se sinta confortável.",
            "Procure apoio profissional se houver preocupação com sua saúde mental.",
        ]

        when_to_seek_help = (
            "Procure ajuda sempre que houver sofrimento intenso, persistente "
            "ou dificuldade para realizar atividades cotidianas."
        )

    return {
        "classification": classification,
        "summary": summary,
        "observed_signs": observed_signs,
        "educational_information": educational_information,
        "recommendations": recommendations,
        "when_to_seek_help": when_to_seek_help,
        "sources": [
            "Organização Mundial da Saúde — mhGAP",
            "Ministério da Saúde",
            "Centro de Valorização da Vida",
        ],
        "disclaimer": (
            "Esta análise possui finalidade educativa e não substitui "
            "avaliação médica ou psicológica."
        ),
    }


def get_stats() -> dict[str, Any]:
    if not os.path.exists(DATASET_PATH):
        return {
            "total_records": 0,
            "total_columns": 0,
            "columns": [],
            "tag_distribution": {},
            "average_text_length": 0.0,
            "minimum_text_length": 0,
            "maximum_text_length": 0,
            "dataset_found": False,
        }

    try:
        dataframe = pd.read_csv(DATASET_PATH)

    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return {
            "total_records": 0,
            "total_columns": 0,
            "columns": [],
            "tag_distribution": {},
            "average_text_length": 0.0,
            "minimum_text_length": 0,
            "maximum_text_length": 0,
            "dataset_found": True,
        }

    text_column = None

    for candidate in [
        "post_content",
        "text",
        "content",
        "message",
    ]:
        if candidate in dataframe.columns:
            text_column = candidate
            break

    if text_column:
        text_lengths = (
            dataframe[text_column]
            .fillna("")
            .astype(str)
            .str.len()
        )

        average_text_length = round(
            float(text_lengths.mean()),
            4,
        )

        minimum_text_length = int(
            text_lengths.min()
        )

        maximum_text_length = int(
            text_lengths.max()
        )

    else:
        average_text_length = 0.0
        minimum_text_length = 0
        maximum_text_length = 0

    if "tag" in dataframe.columns:
        tag_distribution = {
            str(tag): int(count)
            for tag, count in (
                dataframe["tag"]
                .fillna("Sem classificação")
                .value_counts()
                .to_dict()
                .items()
            )
        }

    else:
        tag_distribution = {}

    return {
        "total_records": int(len(dataframe)),
        "total_columns": int(len(dataframe.columns)),
        "columns": dataframe.columns.tolist(),
        "tag_distribution": tag_distribution,
        "average_text_length": average_text_length,
        "minimum_text_length": minimum_text_length,
        "maximum_text_length": maximum_text_length,
        "dataset_found": True,
    }