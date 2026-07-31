"""Orquestrador principal das respostas da Zophia Lite.

Este módulo mantém as funções públicas originais e delega responsabilidades
para serviços menores, sem alterar o fluxo da aplicação.
"""

from backend.services.rag_service import search_documents
from backend.services.conversation_service import conversation_manager
from backend.services.router import Intent, route_message
from backend.services.crisis_service import (
    _crisis_continuation_response,
    _crisis_response,
    _is_crisis_message,
)
from backend.services.ollama_service import (
    MODEL_NAME,
    OLLAMA_URL,
    _call_ollama,
    _general_response,
)
from backend.services.prompts import SYSTEM_PROMPT
from backend.services.rag_context_service import (
    _build_document_context,
    _build_user_prompt,
    _extract_result_value,
)
from backend.services.response_service import (
    _about_zophia_response,
    _datetime_response,
    _general_llm_request_response,
    _goodbye_response,
    _greeting_response,
    _is_general_llm_request,
    _is_goodbye,
    _is_greeting,
    _is_health_mental_question,
    _is_thanks,
    _is_vague_message,
    _out_of_scope_response,
    _thanks_response,
    _vague_message_response,
)
from backend.services.text_utils import _contains_term, _normalize_message

async def generate_response(
    question: str,
    conversation_id: str | None = None,
) -> dict[str, str]:
    """Gera a resposta usando o roteador antes de qualquer consulta ao RAG."""
    question = question.strip()

    conversation = conversation_manager.get_or_create_conversation(
        conversation_id
    )
    current_conversation_id = conversation.conversation_id

    if not question:
        return {
            "response": "Digite uma mensagem para que eu possa ajudar.",
            "conversation_id": current_conversation_id,
        }

    conversation_manager.add_message(
        conversation_id=current_conversation_id,
        role="user",
        content=question,
    )

    history = conversation_manager.build_history(
        conversation_id=current_conversation_id,
        exclude_last_user_message=True,
    )
    has_history = bool(history.strip())
    crisis_active = conversation_manager.is_crisis_active(
        current_conversation_id
    )

    route = route_message(
        question,
        has_conversation_history=has_history,
        crisis_active=crisis_active,
    )
    print(
        f"[ROUTER] intent={route.intent.value} | reason={route.reason}"
    )

    if route.intent == Intent.CRISIS:
        if _is_crisis_message(question):
            conversation_manager.set_crisis_active(
                current_conversation_id, True
            )
            response = _crisis_response()
        else:
            response = _crisis_continuation_response(question)

    elif route.intent == Intent.DATETIME:
        response = _datetime_response(question)

    elif route.intent == Intent.ABOUT_ZOPHIA:
        response = _about_zophia_response()

    elif route.intent == Intent.GREETING:
        response = _greeting_response(question)

    elif route.intent == Intent.THANKS:
        response = _thanks_response()

    elif route.intent == Intent.GOODBYE:
        response = _goodbye_response()

    elif route.intent == Intent.MEMORY:
        response = _general_response(question, history)

    elif route.intent == Intent.GENERAL:
        response = _general_response(question, history)

    else:
        # Somente saúde mental e continuações contextuais chegam ao RAG.
        search_query = conversation_manager.build_search_query(
            conversation_id=current_conversation_id,
            current_question=question,
            previous_user_messages=2,
        )

        try:
            rag_results = await search_documents(
                question=search_query,
                limit=3,
            )
        except TypeError:
            rag_results = await search_documents(search_query)
        except Exception as error:
            print(f"Erro durante a busca no RAG: {error}")
            rag_results = {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        document_context = _build_document_context(rag_results)
        user_prompt = _build_user_prompt(
            question=question,
            document_context=document_context,
            conversation_history=history,
        )
        response = _call_ollama(user_prompt)

    conversation_manager.add_message(
        conversation_id=current_conversation_id,
        role="assistant",
        content=response,
    )

    return {
        "response": response,
        "conversation_id": current_conversation_id,
    }

async def generate_llm_response(
    question: str,
    conversation_id: str | None = None,
) -> dict[str, str]:
    return await generate_response(
        question=question,
        conversation_id=conversation_id,
    )

async def get_llm_response(
    question: str,
    conversation_id: str | None = None,
) -> dict[str, str]:
    return await generate_response(
        question=question,
        conversation_id=conversation_id,
    )

