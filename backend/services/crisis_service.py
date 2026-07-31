"""Detecção e respostas do fluxo de crise da Zophia Lite."""

from backend.services.text_utils import _normalize_message

CRISIS_EXPRESSIONS = {
    "quero morrer",
    "quero me matar",
    "vou me matar",
    "quero tirar minha vida",
    "vou tirar minha vida",
    "nao quero mais viver",
    "não quero mais viver",
    "seria melhor morrer",
    "queria estar morto",
    "queria estar morta",
    "penso em suicidio",
    "penso em suicídio",
    "estou pensando em me matar",
    "estou pensando em morrer",
    "vou acabar com tudo",
    "quero desaparecer para sempre",
    "nao aguento mais viver",
    "não aguento mais viver",
    "pretendo me matar",
    "tenho um plano para me matar",
    "vou me machucar",
    "quero me machucar",
}

AFFIRMATIVE_MESSAGES = {
    "sim",
    "s",
    "claro",
    "consigo",
    "posso",
    "ja chamei",
    "já chamei",
    "tem alguem comigo",
    "tem alguém comigo",
    "estou com alguem",
    "estou com alguém",
}

NEGATIVE_MESSAGES = {
    "nao",
    "não",
    "n",
    "nao consigo",
    "não consigo",
    "nao tenho ninguem",
    "não tenho ninguém",
    "estou sozinho",
    "estou sozinha",
    "ninguem",
    "ninguém",
}

def _is_crisis_message(message: str) -> bool:
    """
    Identifica mensagens com possível risco imediato de suicídio
    ou autoagressão.
    """

    normalized_message = _normalize_message(message)

    normalized_expressions = {
        _normalize_message(expression)
        for expression in CRISIS_EXPRESSIONS
    }

    return any(
        expression in normalized_message
        for expression in normalized_expressions
    )

def _crisis_response() -> str:
    """
    Retorna apoio imediato sem consultar documentos ou a LLM.
    """

    return (
        "Sinto muito que você esteja passando por isso. "
        "Você não precisa enfrentar esse momento sozinho.\n\n"
        "Você corre risco de se machucar agora ou já preparou alguma forma "
        "de fazer isso?\n\n"
        "Se o risco for imediato, afaste-se de qualquer objeto ou situação "
        "que possa machucar você e procure agora uma pessoa de confiança, "
        "um pronto atendimento ou um serviço de emergência.\n\n"
        "No Brasil, você também pode conversar gratuitamente com o CVV "
        "pelo número 188, disponível 24 horas.\n\n"
        "Enquanto busca ajuda, permaneça perto de alguém. "
        "Você consegue chamar uma pessoa de confiança agora?"
    )

def _is_affirmative_message(message: str) -> bool:
    normalized_message = _normalize_message(message)

    return normalized_message in {
        _normalize_message(item)
        for item in AFFIRMATIVE_MESSAGES
    }

def _is_negative_message(message: str) -> bool:
    normalized_message = _normalize_message(message)

    return normalized_message in {
        _normalize_message(item)
        for item in NEGATIVE_MESSAGES
    }

def _crisis_affirmative_response() -> str:
    return (
        "Obrigado por me responder. Chame essa pessoa agora e diga "
        "claramente que você não está se sentindo seguro e precisa que "
        "ela permaneça com você.\n\n"
        "Afaste-se de qualquer objeto, medicamento ou lugar que possa "
        "colocar você em risco. Se você estiver prestes a se machucar "
        "ou já tiver feito algo, procure imediatamente um pronto "
        "atendimento ou ligue para o serviço de emergência.\n\n"
        "Você já chamou essa pessoa ou ela está com você agora?"
    )

def _crisis_negative_response() -> str:
    return (
        "Sinto muito que você esteja sozinho neste momento. "
        "Vamos priorizar sua segurança agora.\n\n"
        "Afaste-se de qualquer objeto, medicamento ou lugar que possa "
        "machucar você e vá para um ambiente com outras pessoas, como "
        "uma recepção, portaria, comércio, unidade de saúde ou casa "
        "de alguém próximo.\n\n"
        "Ligue gratuitamente para o CVV pelo número 188. "
        "Se houver risco imediato, procure um pronto atendimento ou "
        "acione o serviço de emergência.\n\n"
        "Você consegue ir agora para um lugar onde haja outra pessoa?"
    )

def _crisis_continuation_response(
    message: str,
) -> str:
    """
    Gera uma resposta segura para mensagens enviadas enquanto
    uma situação de crise permanece ativa.
    """

    if _is_affirmative_message(message):
        return _crisis_affirmative_response()

    if _is_negative_message(message):
        return _crisis_negative_response()

    return (
        "Obrigado por continuar falando comigo. "
        "O mais importante agora é não ficar sozinho e reduzir qualquer "
        "risco ao seu redor.\n\n"
        "Você está em perigo imediato ou tem acesso agora a algo que "
        "poderia usar para se machucar?\n\n"
        "Procure uma pessoa de confiança, um pronto atendimento ou um "
        "serviço de emergência. No Brasil, você também pode conversar "
        "gratuitamente com o CVV pelo número 188."
    )

