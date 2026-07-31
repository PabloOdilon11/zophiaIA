"""Respostas determinísticas e verificações simples da Zophia Lite."""

from datetime import datetime

from backend.services.prompts import GENERAL_LLM_REQUESTS, HEALTH_TERMS, VAGUE_MESSAGES
from backend.services.text_utils import _contains_term, _normalize_message

def _is_greeting(message: str) -> bool:
    """
    Identifica mensagens que são apenas saudações.
    """

    normalized_message = _normalize_message(message)

    greetings = {
        "oi",
        "ola",
        "opa",
        "eai",
        "e ai",
        "bom dia",
        "boa tarde",
        "boa noite",
        "tudo bem",
        "como vai",
        "oi tudo bem",
        "ola tudo bem",
        "oi como vai",
        "ola como vai",
    }

    return normalized_message in {
        _normalize_message(item)
        for item in greetings
    }

def _greeting_response(message: str) -> str:
    """
    Retorna uma saudação sem consultar o RAG.
    """

    normalized_message = _normalize_message(message)

    if "bom dia" in normalized_message:
        greeting = "Bom dia"

    elif "boa tarde" in normalized_message:
        greeting = "Boa tarde"

    elif "boa noite" in normalized_message:
        greeting = "Boa noite"

    else:
        greeting = "Olá"

    return (
        f"{greeting}! Eu sou a Zophia, uma assistente virtual "
        "educativa de apoio à saúde mental. "
        "Como posso ajudar você hoje?"
    )

def _is_thanks(message: str) -> bool:
    """
    Identifica agradecimentos simples.
    """

    normalized_message = _normalize_message(message)

    thanks_messages = {
        "obrigado",
        "obrigada",
        "valeu",
        "muito obrigado",
        "muito obrigada",
        "agradeco",
    }

    return normalized_message in {
        _normalize_message(item)
        for item in thanks_messages
    }

def _thanks_response() -> str:
    """
    Retorna uma resposta para agradecimentos.
    """

    return (
        "Por nada! Fico feliz em ajudar. "
        "Sempre que precisar conversar ou buscar "
        "informações educativas, estou aqui."
    )

def _is_goodbye(message: str) -> bool:
    """
    Identifica despedidas simples.
    """

    normalized_message = _normalize_message(message)

    goodbye_messages = {
        "tchau",
        "ate mais",
        "ate logo",
        "falou",
        "vou sair",
        "boa noite tchau",
    }

    return normalized_message in {
        _normalize_message(item)
        for item in goodbye_messages
    }

def _goodbye_response() -> str:
    """
    Retorna uma resposta para despedidas.
    """

    return (
        "Até mais! Cuide-se e lembre-se de que buscar apoio "
        "quando necessário é uma atitude importante."
    )

def _is_general_llm_request(message: str) -> bool:
    """
    Identifica pedidos para ignorar os documentos e utilizar
    o conhecimento geral da LLM.
    """

    normalized_message = _normalize_message(message)

    normalized_requests = {
        _normalize_message(item)
        for item in GENERAL_LLM_REQUESTS
    }

    if normalized_message in normalized_requests:
        return True

    return any(
        request in normalized_message
        for request in normalized_requests
    )

def _general_llm_request_response() -> str:
    """
    Evita que um comando vago seja pesquisado no banco vetorial.
    """

    return (
        "A Zophia foi configurada para oferecer informações sobre "
        "saúde mental com base na documentação disponível. Também não "
        "consigo identificar, somente por essa mensagem, qual pergunta "
        "anterior você deseja que seja respondida. Envie novamente a "
        "pergunta completa."
    )

def _is_vague_message(message: str) -> bool:
    """
    Identifica mensagens que dependem de uma pergunta anterior
    e não possuem assunto suficiente para uma busca segura.
    """

    normalized_message = _normalize_message(message)

    normalized_vague_messages = {
        _normalize_message(item)
        for item in VAGUE_MESSAGES
    }

    return normalized_message in normalized_vague_messages

def _vague_message_response() -> str:
    """
    Solicita que a pergunta seja enviada novamente de forma completa.
    """

    return (
        "Não consegui identificar com segurança o assunto da mensagem. "
        "Escreva novamente a pergunta completa para que eu não recupere "
        "informações sem relação com o que você deseja saber."
    )

def _is_health_mental_question(message: str) -> bool:
    """
    Verifica se a mensagem apresenta algum termo relacionado
    ao escopo de saúde mental da Zophia.
    """

    normalized_message = _normalize_message(message)

    return any(
        _contains_term(
            normalized_message,
            term,
        )
        for term in HEALTH_TERMS
    )

def _out_of_scope_response() -> str:
    """
    Resposta utilizada para perguntas fora do escopo.
    """

    return (
        "Essa pergunta está fora do escopo da Zophia. "
        "Minha base documental é voltada à educação e ao apoio "
        "em saúde mental. Posso ajudar com temas como ansiedade, "
        "depressão, estresse, sono, bem-estar emocional e busca "
        "por apoio profissional."
    )

def _about_zophia_response() -> str:
    """Responde sobre a identidade da Zophia sem consultar RAG ou LLM."""
    return (
        "Eu sou a Zophia Lite, uma assistente virtual educativa de apoio à "
        "saúde mental. Fui desenvolvida como um projeto acadêmico por um "
        "grupo de estudantes do curso de Ciência da Computação da "
        "Universidade Estadual da Paraíba (UEPB).\n\n"
        "Meu objetivo é oferecer informações educativas de forma clara, "
        "acolhedora e responsável. Minha aplicação utiliza React no frontend, "
        "FastAPI no backend, o modelo Gemma 3 4B executado localmente pelo "
        "Ollama, ChromaDB, embeddings, Recuperação Aumentada por Geração "
        "(RAG) e memória de conversa.\n\n"
        "Não sou o ChatGPT e não fui criada pela OpenAI, pelo Google, pelo "
        "Ollama, pelo Gemma nem pelos autores dos documentos da minha base. "
        "Também não substituo psicólogos, psiquiatras, médicos ou serviços "
        "de emergência."
    )

def _datetime_response(question: str) -> str:
    """Responde data e hora usando o relógio do servidor, sem RAG ou LLM."""
    now = datetime.now()
    normalized = _normalize_message(question)

    weekdays = (
        "segunda-feira", "terça-feira", "quarta-feira",
        "quinta-feira", "sexta-feira", "sábado", "domingo",
    )
    months = (
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    )

    asks_time = "hora" in normalized or "horario" in normalized
    asks_date = any(term in normalized for term in (
        "data", "dia", "mes", "ano", "semana", "hoje"
    ))

    time_text = f"Agora são {now:%H:%M}."
    date_text = (
        f"Hoje é {weekdays[now.weekday()]}, "
        f"{now.day} de {months[now.month - 1]} de {now.year}."
    )

    if asks_time and asks_date:
        return f"{date_text} {time_text}"
    if asks_time:
        return time_text
    return date_text

