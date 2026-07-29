"""
Roteador de intenções da Zophia Lite.

Este módulo classifica cada mensagem antes que ela seja enviada para:
- respostas prontas;
- memória da conversa;
- data e hora;
- fluxo de crise;
- modelo geral;
- RAG de saúde mental.

A classificação é determinística e não depende do Ollama.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class Intent(str, Enum):
    EMPTY = "empty"
    CRISIS = "crisis"
    GREETING = "greeting"
    THANKS = "thanks"
    GOODBYE = "goodbye"
    MEMORY = "memory"
    DATETIME = "datetime"
    ABOUT_ZOPHIA = "about_zophia"
    CONTEXT_FOLLOW_UP = "context_follow_up"
    MENTAL_HEALTH = "mental_health"
    GENERAL = "general"


@dataclass(frozen=True)
class RouteResult:
    intent: Intent
    normalized_message: str
    reason: str


def normalize_text(text: str) -> str:
    """
    Normaliza texto para comparação:
    - remove espaços extras;
    - converte para minúsculas;
    - remove acentos;
    - mantém letras, números e sinais matemáticos úteis.
    """
    text = " ".join((text or "").strip().lower().split())

    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    normalized = re.sub(
        r"[^a-z0-9\s+\-*/%=?.!,]",
        " ",
        normalized,
    )

    return " ".join(normalized.split())


def _contains_phrase(message: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in message for phrase in phrases)


def _matches_full_message(
    message: str,
    patterns: tuple[str, ...],
) -> bool:
    clean_message = message.strip(" ?!.,")
    return any(
        re.fullmatch(pattern, clean_message) is not None
        for pattern in patterns
    )


CRISIS_PHRASES = (
    "quero me matar",
    "vou me matar",
    "pensando em me matar",
    "penso em me matar",
    "queria morrer",
    "quero morrer",
    "nao quero mais viver",
    "nao aguento mais viver",
    "vou tirar minha vida",
    "tirar a minha vida",
    "acabar com minha vida",
    "acabar com a minha vida",
    "me suicidar",
    "cometer suicidio",
    "planejando suicidio",
    "tenho um plano para morrer",
    "estou prestes a me machucar",
    "vou me machucar",
    "quero me machucar",
    "me cortar",
    "vou me cortar",
    "estou em risco agora",
)

GREETING_PATTERNS = (
    r"ola",
    r"oi",
    r"opa",
    r"e ai",
    r"ei",
    r"bom dia",
    r"boa tarde",
    r"boa noite",
    r"tudo bem",
    r"como vai",
    r"ola zophia",
    r"oi zophia",
)

THANKS_PATTERNS = (
    r"obrigad[oa]",
    r"muito obrigad[oa]",
    r"valeu",
    r"agradeco",
    r"gratidao",
    r"perfeito",
    r"entendi",
)

GOODBYE_PATTERNS = (
    r"tchau",
    r"ate mais",
    r"ate logo",
    r"ate depois",
    r"falou",
    r"vou embora",
    r"encerrar conversa",
    r"encerrar o chat",
)

MEMORY_PHRASES = (
    "qual foi a primeira mensagem",
    "qual foi minha primeira mensagem",
    "o que eu disse primeiro",
    "o que eu falei primeiro",
    "primeira coisa que eu disse",
    "primeira coisa que eu falei",
    "qual foi a ultima mensagem",
    "qual foi minha ultima mensagem",
    "o que eu perguntei antes",
    "o que eu falei antes",
    "o que eu disse antes",
    "minha mensagem anterior",
    "minha pergunta anterior",
    "voce lembra",
    "lembra do que eu disse",
    "lembra do que eu falei",
    "lembra da nossa conversa",
    "resuma nossa conversa",
    "resuma o que conversamos",
    "sobre o que conversamos",
    "qual era o assunto anterior",
    "qual assunto estavamos falando",
    "o que voce respondeu antes",
)

DATETIME_PHRASES = (
    "que dia e hoje",
    "qual e o dia de hoje",
    "qual a data de hoje",
    "data de hoje",
    "em que dia estamos",
    "que horas sao",
    "qual e a hora",
    "qual a hora agora",
    "horario agora",
    "que horas e",
    "qual e o mes atual",
    "em que mes estamos",
    "qual e o ano atual",
    "em que ano estamos",
    "qual dia da semana",
    "que dia da semana e hoje",
)


ABOUT_ZOPHIA_PHRASES = (
    "quem e voce",
    "quem criou voce",
    "quem te criou",
    "quem desenvolveu voce",
    "quem te desenvolveu",
    "quem fez voce",
    "quem criou a zophia",
    "quem desenvolveu a zophia",
    "voce e da openai",
    "voce foi criada pela openai",
    "voce foi desenvolvido pela openai",
    "voce e o chatgpt",
    "voce e chatgpt",
    "voce e da google",
    "voce foi criada pela google",
    "qual modelo voce usa",
    "qual tecnologia voce usa",
    "como voce funciona",
    "o que e a zophia",
    "o que e zophia lite",
)

CONTEXT_FOLLOW_UP_PATTERNS = (
    r"continue",
    r"continua",
    r"pode continuar",
    r"explique melhor",
    r"explica melhor",
    r"detalhe mais",
    r"fale mais",
    r"me diga mais",
    r"e isso",
    r"e sobre isso",
    r"como assim",
    r"por que",
    r"porque",
    r"e depois",
    r"e quanto tempo",
    r"e quais sao",
    r"quais",
)

MENTAL_HEALTH_TERMS = (
    "saude mental",
    "ansiedade",
    "ansioso",
    "ansiosa",
    "crise de ansiedade",
    "ataque de panico",
    "panico",
    "depressao",
    "depressivo",
    "depressiva",
    "tristeza profunda",
    "estresse",
    "stress",
    "burnout",
    "esgotamento",
    "trauma",
    "traumatico",
    "traumatica",
    "transtorno",
    "transtorno mental",
    "transtorno bipolar",
    "bipolaridade",
    "esquizofrenia",
    "psicose",
    "toc",
    "transtorno obsessivo compulsivo",
    "tdah",
    "autismo",
    "tea",
    "fobia",
    "agorafobia",
    "fobia social",
    "insonia",
    "sono",
    "pesadelo",
    "luto",
    "culpa",
    "autoestima",
    "solidao",
    "isolamento",
    "emocao",
    "emocional",
    "psicologo",
    "psicologa",
    "psiquiatra",
    "psiquiatria",
    "psicologia",
    "terapia",
    "terapeuta",
    "medicacao psiquiatrica",
    "antidepressivo",
    "ansiolitico",
    "saude emocional",
    "bem estar emocional",
    "automutilacao",
    "autolesao",
    "suicidio",
    "suicida",
    "ideacao suicida",
    "pensamentos intrusivos",
    "compulsao",
    "dependencia emocional",
    "abuso emocional",
    "violencia psicologica",
)


def is_crisis_message(message: str) -> bool:
    normalized = normalize_text(message)
    return _contains_phrase(normalized, CRISIS_PHRASES)


def is_greeting(message: str) -> bool:
    normalized = normalize_text(message)
    return _matches_full_message(normalized, GREETING_PATTERNS)


def is_thanks(message: str) -> bool:
    normalized = normalize_text(message)
    return _matches_full_message(normalized, THANKS_PATTERNS)


def is_goodbye(message: str) -> bool:
    normalized = normalize_text(message)
    return _matches_full_message(normalized, GOODBYE_PATTERNS)


def is_memory_question(message: str) -> bool:
    normalized = normalize_text(message)
    return _contains_phrase(normalized, MEMORY_PHRASES)


def is_datetime_question(message: str) -> bool:
    normalized = normalize_text(message)
    return _contains_phrase(normalized, DATETIME_PHRASES)


def is_about_zophia_question(message: str) -> bool:
    normalized = normalize_text(message)
    return _contains_phrase(normalized, ABOUT_ZOPHIA_PHRASES)


def is_context_follow_up(message: str) -> bool:
    normalized = normalize_text(message)

    if _matches_full_message(
        normalized,
        CONTEXT_FOLLOW_UP_PATTERNS,
    ):
        return True

    reference_terms = (
        "isso",
        "esse assunto",
        "essa situacao",
        "esse problema",
        "o assunto anterior",
        "a resposta anterior",
    )

    return (
        len(normalized.split()) <= 12
        and _contains_phrase(normalized, reference_terms)
    )


def is_mental_health_question(message: str) -> bool:
    normalized = normalize_text(message)

    for term in MENTAL_HEALTH_TERMS:
        normalized_term = normalize_text(term)

        if re.search(
            rf"(?<!\w){re.escape(normalized_term)}(?!\w)",
            normalized,
        ):
            return True

    return False


def route_message(
    message: str,
    *,
    has_conversation_history: bool = False,
    crisis_active: bool = False,
) -> RouteResult:
    """
    Classifica uma mensagem usando uma ordem de prioridade segura.

    Ordem:
    1. mensagem vazia;
    2. crise atual ou crise já ativa;
    3. memória;
    4. data/hora;
    5. identidade da Zophia;
    6. saudação, agradecimento ou despedida;
    7. continuação contextual;
    8. saúde mental;
    9. conhecimento geral.
    """
    normalized = normalize_text(message)

    if not normalized:
        return RouteResult(
            intent=Intent.EMPTY,
            normalized_message=normalized,
            reason="A mensagem está vazia.",
        )

    if is_crisis_message(normalized):
        return RouteResult(
            intent=Intent.CRISIS,
            normalized_message=normalized,
            reason="A mensagem contém indicação explícita de risco.",
        )

    if crisis_active:
        return RouteResult(
            intent=Intent.CRISIS,
            normalized_message=normalized,
            reason="A conversa possui um fluxo de crise ativo.",
        )

    if is_memory_question(normalized):
        return RouteResult(
            intent=Intent.MEMORY,
            normalized_message=normalized,
            reason="A pergunta solicita informações do histórico.",
        )

    if is_datetime_question(normalized):
        return RouteResult(
            intent=Intent.DATETIME,
            normalized_message=normalized,
            reason="A pergunta solicita data ou hora atual.",
        )

    if is_about_zophia_question(normalized):
        return RouteResult(
            intent=Intent.ABOUT_ZOPHIA,
            normalized_message=normalized,
            reason="A pergunta solicita informações sobre a identidade da Zophia.",
        )

    if is_greeting(normalized):
        return RouteResult(
            intent=Intent.GREETING,
            normalized_message=normalized,
            reason="A mensagem é uma saudação.",
        )

    if is_thanks(normalized):
        return RouteResult(
            intent=Intent.THANKS,
            normalized_message=normalized,
            reason="A mensagem é um agradecimento.",
        )

    if is_goodbye(normalized):
        return RouteResult(
            intent=Intent.GOODBYE,
            normalized_message=normalized,
            reason="A mensagem é uma despedida.",
        )

    if (
        has_conversation_history
        and is_context_follow_up(normalized)
    ):
        return RouteResult(
            intent=Intent.CONTEXT_FOLLOW_UP,
            normalized_message=normalized,
            reason=(
                "A mensagem depende do contexto anterior "
                "da conversa."
            ),
        )

    if is_mental_health_question(normalized):
        return RouteResult(
            intent=Intent.MENTAL_HEALTH,
            normalized_message=normalized,
            reason=(
                "A mensagem pertence ao domínio de saúde mental "
                "e pode consultar o RAG."
            ),
        )

    return RouteResult(
        intent=Intent.GENERAL,
        normalized_message=normalized,
        reason=(
            "A mensagem não pertence às rotas especiais "
            "nem ao domínio de saúde mental."
        ),
    )


def classify_intent(
    message: str,
    *,
    has_conversation_history: bool = False,
    crisis_active: bool = False,
) -> Intent:
    """Atalho para obter apenas a intenção."""
    return route_message(
        message,
        has_conversation_history=has_conversation_history,
        crisis_active=crisis_active,
    ).intent