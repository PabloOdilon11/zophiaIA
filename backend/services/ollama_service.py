"""Comunicação com o Ollama e geração de respostas gerais."""

import requests

from backend.services.prompts import SYSTEM_PROMPT

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:4b"

def _call_ollama(
    user_prompt: str,
) -> str:
    """
    Envia o prompt para o Gemma 3 pelo Ollama.
    """

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{user_prompt}"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.85,
            "top_k": 20,
            "repeat_penalty": 1.15,
            "num_predict": 280,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        generated_response = data.get(
            "response",
            "",
        ).strip()

        if not generated_response:
            return (
                "Não consegui gerar uma resposta neste momento. "
                "Tente novamente em alguns instantes."
            )

        # Remove prefixos que o modelo pode adicionar indevidamente.
        unwanted_prefixes = (
            "Zophia:",
            "Assistente:",
            "Assistant:",
            "Resposta:",
        )

        for prefix in unwanted_prefixes:
            if generated_response.lower().startswith(prefix.lower()):
                generated_response = generated_response[len(prefix):].strip()
                break

        return generated_response

    except requests.exceptions.ConnectionError:
        return (
            "Não foi possível conectar ao Ollama. "
            "Verifique se ele está em execução."
        )

    except requests.exceptions.Timeout:
        return (
            "A geração da resposta demorou mais que o esperado. "
            "Tente novamente."
        )

    except requests.exceptions.RequestException as error:
        print(
            f"Erro ao consultar o Ollama: {error}"
        )

        return (
            "Ocorreu um erro ao gerar a resposta. "
            "Tente novamente em alguns instantes."
        )

    except ValueError as error:
        print(
            "O Ollama retornou uma resposta JSON inválida: "
            f"{error}"
        )

        return (
            "O serviço de geração retornou uma resposta inválida. "
            "Tente novamente em alguns instantes."
        )

def _general_response(question: str, conversation_history: str) -> str:
    """Responde perguntas gerais sem consultar o banco vetorial."""
    prompt = f"""
HISTÓRICO RECENTE DA CONVERSA:
{conversation_history or 'Nenhum histórico anterior.'}

MENSAGEM ATUAL DO USUÁRIO:
{question}

Responda de forma natural, clara e objetiva. Não use nem mencione documentos,
RAG, banco vetorial, páginas ou trechos. Não invente que documentos ou seus
autores criaram a Zophia. Caso a pergunta seja médica ou psicológica, mantenha
os limites educativos e não faça diagnóstico nem prescrição.
""".strip()
    return _call_ollama(prompt)

