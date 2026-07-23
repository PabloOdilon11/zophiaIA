import os
from typing import Any

import httpx

from backend.services.rag_service import search_documents


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat",
)

MODEL_NAME = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b",
)

REQUEST_TIMEOUT = 120.0


SYSTEM_PROMPT = """
Você é a Zophia, uma assistente virtual educacional especializada em
acolhimento emocional, bem-estar e educação em saúde mental.

IDENTIDADE E ESCOPO
- Responda sempre em português brasileiro.
- Atue somente em assuntos relacionados a emoções, saúde mental,
  autocuidado, relacionamentos, rotina, sono, ansiedade, estresse,
  tristeza, depressão, apoio emocional e busca de ajuda.
- Perguntas sobre ansiedade, depressão, estresse, sono, tristeza,
  suicídio, medicamentos psiquiátricos e transtornos mentais estão
  dentro do seu escopo.
- Nunca use a resposta de fora do escopo em uma pergunta relacionada
  à saúde mental.
- Quando a pergunta realmente estiver fora desse escopo, responda
  somente:
  "Meu foco é acolhimento emocional e educação em saúde mental.
  Posso ajudar você com sentimentos, ansiedade, estresse, rotina,
  sono ou bem-estar."

USO DOS DOCUMENTOS
- Quando receber contexto documental, use-o como principal fonte.
- Antes de responder, verifique se os trechos realmente respondem
  à pergunta do usuário.
- Ignore trechos que apenas mencionem assuntos parecidos, mas que
  não respondam diretamente à pergunta.
- Não invente informações para completar um contexto insuficiente.
- Não invente fontes, páginas, autores ou nomes de documentos.
- Explique as informações dos documentos com palavras simples.
- Cite somente documentos que tenham sido realmente utilizados.
- Caso nenhum trecho seja útil, informe que a base documental não
  encontrou informação suficiente para uma resposta baseada em fontes.

PRECISÃO E CONFIABILIDADE
- Nunca invente fatos, fontes, pesquisas, estatísticas ou acontecimentos.
- Nunca apresente uma suposição como verdade.
- Quando não possuir segurança, informe isso claramente.
- Não crie nomes de profissionais, instituições, tratamentos ou remédios.
- Não afirme que uma informação está em um documento quando ela não está.
- Não tente preencher lacunas usando imaginação.

SEGURANÇA EM SAÚDE
- Não faça diagnóstico médico, psicológico ou psiquiátrico.
- Não afirme que o usuário possui uma doença ou transtorno.
- Não prescreva, indique, suspenda ou altere medicamentos.
- Não recomende doses ou combinações de medicamentos.
- Não substitua psicólogos, psiquiatras, médicos ou emergências.
- Apresente o conteúdo como informação educativa.
- Incentive ajuda profissional quando o sofrimento for intenso,
  persistente ou estiver prejudicando a rotina.
- Não minimize sentimentos e não culpe o usuário.
- Não incentive dependência emocional em relação à assistente.
- Não diga que é a única companhia do usuário.
- Não diga que estará sempre disponível de forma pessoal.

SITUAÇÕES DE RISCO
- Se houver menção a suicídio, automutilação, desejo de morrer,
  violência, abuso, overdose ou perigo imediato:
  1. Responda com acolhimento e seriedade.
  2. Oriente a pessoa a não permanecer sozinha.
  3. Incentive contato imediato com alguém de confiança.
  4. Recomende procurar um serviço de emergência da região.
  5. Não forneça instruções que possam facilitar dano.
  6. Pergunte de forma curta se existe perigo imediato.
- Não trate situações de risco como uma conversa comum.
- As instruções de segurança possuem prioridade sobre os documentos.

FORMA DA RESPOSTA
- Use linguagem acolhedora, clara, natural e respeitosa.
- Evite respostas excessivamente longas.
- Não use tom infantilizado.
- Evite muitos emojis.
- Não diga que realizou avaliação clínica.
- Não apresente certezas médicas.
- Ofereça ações simples, seguras e realistas quando apropriado.
"""


def _validate_message(message: str) -> str:
    if not isinstance(message, str):
        raise ValueError(
            "A mensagem deve ser um texto."
        )

    clean_message = message.strip()

    if not clean_message:
        raise ValueError(
            "A mensagem não pode estar vazia."
        )

    if len(clean_message) > 8_000:
        raise ValueError(
            "A mensagem é muito extensa. Envie um texto menor."
        )

    return clean_message


def _extract_content(data: Any) -> str:
    if not isinstance(data, dict):
        raise RuntimeError(
            "A resposta recebida do Ollama não é válida."
        )

    message_data = data.get("message")

    if not isinstance(message_data, dict):
        raise RuntimeError(
            "A resposta do Ollama não contém o campo 'message'."
        )

    content = message_data.get("content")

    if not isinstance(content, str):
        raise RuntimeError(
            "A resposta do Ollama não contém texto válido."
        )

    clean_content = content.strip()

    if not clean_content:
        raise RuntimeError(
            "O Ollama retornou uma resposta vazia."
        )

    return clean_content


def _build_document_context(
    results: dict[str, Any],
) -> str:
    """
    Converte os resultados do ChromaDB em um contexto organizado
    para a Gemma.
    """

    documents_groups = results.get(
        "documents",
        [[]],
    )

    metadatas_groups = results.get(
        "metadatas",
        [[]],
    )

    distances_groups = results.get(
        "distances",
        [[]],
    )

    documents = (
        documents_groups[0]
        if documents_groups
        else []
    )

    metadatas = (
        metadatas_groups[0]
        if metadatas_groups
        else []
    )

    distances = (
        distances_groups[0]
        if distances_groups
        else []
    )

    if not documents:
        return ""

    context_parts: list[str] = []

    for index, document in enumerate(documents):
        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        source = metadata.get(
            "source",
            "Documento não informado",
        )

        page = metadata.get(
            "page",
            "não informada",
        )

        context_part = (
            f"[TRECHO {index + 1}]\n"
            f"Fonte: {source}\n"
            f"Página: {page}\n"
        )

        if isinstance(distance, (int, float)):
            context_part += (
                f"Distância semântica: {distance:.4f}\n"
            )

        context_part += (
            f"Conteúdo:\n{document.strip()}"
        )

        context_parts.append(context_part)

    return "\n\n".join(context_parts)


def _build_user_prompt(
    question: str,
    document_context: str,
) -> str:
    """
    Monta a mensagem enviada para a Gemma.
    """

    if not document_context:
        return f"""
PERGUNTA DO USUÁRIO:
{question}

RESULTADO DA CONSULTA DOCUMENTAL:
Nenhum trecho suficientemente relevante foi encontrado na base.

INSTRUÇÕES OBRIGATÓRIAS:
- Informe claramente que a base documental não encontrou informações
  suficientes para responder à pergunta.
- Não forneça sintomas, causas, tratamentos, exemplos clínicos ou
  explicações técnicas baseadas no seu conhecimento geral.
- Não complete a resposta com informações que não estejam nos documentos.
- Não cite fontes, pois nenhum trecho relevante foi encontrado.
- Não faça diagnóstico.
- Você pode apenas acolher brevemente e sugerir que a pessoa procure
  um profissional de saúde caso esteja preocupada.
- Mantenha a resposta curta.
""".strip()
    return f"""
CONTEXTO DOCUMENTAL:
{document_context}

PERGUNTA DO USUÁRIO:
{question}

INSTRUÇÕES PARA RESPONDER:
- A pergunta está dentro do escopo quando envolver saúde mental,
  sentimentos, ansiedade, depressão, estresse, sono ou bem-estar.
- Não use a resposta de fora do escopo em perguntas de saúde mental.
- Analise se os trechos realmente respondem à pergunta.
- Ignore qualquer trecho que seja apenas vagamente relacionado.
- Não use informações técnicas que não estejam apoiadas no contexto.
- Explique o conteúdo de forma clara e em português brasileiro.
- Não copie grandes partes dos documentos literalmente.
- Não faça diagnóstico.
- Não indique, suspenda ou altere medicamentos.
- Caso os trechos não respondam à pergunta, diga que a base documental
  não encontrou informação suficientemente direta.
- Ao final, cite somente as fontes realmente utilizadas no formato:
  "Fontes consultadas: arquivo, página."
- Não cite um trecho que tenha sido ignorado durante a resposta.
""".strip()


async def generate_llm_response(
    message: str,
) -> str:
    clean_message = _validate_message(message)

    document_context = ""

    try:
        rag_results = await search_documents(
            question=clean_message,
            limit=3,
        )

        document_context = _build_document_context(
            rag_results
        )
        print("\n========== CONTEXTO ENVIADO ==========\n")
        print(document_context)
        print("\n======================================\n")
    except Exception as error:
        # O chat permanece funcionando mesmo se o RAG falhar.
        print(
            f"Erro ao consultar a base documental: {error}"
        )

    user_prompt = _build_user_prompt(
        question=clean_message,
        document_context=document_context,
    )

    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "options": {
            "temperature": 0.1,
            "top_p": 0.8,
            "repeat_penalty": 1.1,
            "num_predict": 500,
            "num_ctx": 8192,
        },
    }

    timeout = httpx.Timeout(
        connect=10.0,
        read=REQUEST_TIMEOUT,
        write=30.0,
        pool=10.0,
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:
            response = await client.post(
                OLLAMA_URL,
                json=payload,
            )

            response.raise_for_status()

        try:
            data = response.json()

        except ValueError as error:
            raise RuntimeError(
                "O Ollama retornou uma resposta que não é JSON."
            ) from error

        return _extract_content(data)

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Não foi possível conectar ao Ollama. "
            "Verifique se o Ollama está aberto e se o modelo "
            f"'{MODEL_NAME}' está instalado."
        ) from error

    except httpx.ReadTimeout as error:
        raise RuntimeError(
            "O Ollama demorou muito para responder. "
            "Tente novamente com uma mensagem menor."
        ) from error

    except httpx.TimeoutException as error:
        raise RuntimeError(
            "A comunicação com o Ollama excedeu o tempo limite."
        ) from error

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code

        raise RuntimeError(
            f"O Ollama retornou o erro HTTP {status_code}."
        ) from error

    except httpx.RequestError as error:
        raise RuntimeError(
            "Ocorreu uma falha de comunicação com o Ollama."
        ) from error