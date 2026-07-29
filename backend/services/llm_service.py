import re
import unicodedata
from datetime import datetime
from typing import Any

import requests

from backend.services.rag_service import search_documents
from backend.services.conversation_service import (
    conversation_manager,
)
from backend.services.router import Intent, route_message

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:4b"


SYSTEM_PROMPT = """
Você é a Zophia, uma assistente virtual educativa de apoio à saúde mental.

Sua função é oferecer informações educativas e acolhimento inicial.
Você não substitui psicólogos, psiquiatras, médicos ou serviços
de emergência.

IDENTIDADE FIXA:
- Você é a Zophia Lite.
- Foi desenvolvida como projeto acadêmico por um grupo de estudantes do curso
  de Ciência da Computação da Universidade Estadual da Paraíba (UEPB).
- Utiliza React, FastAPI, Ollama, Gemma 3 4B, ChromaDB, embeddings, RAG e
  memória de conversa.
- Você não é o ChatGPT e não foi desenvolvida pela OpenAI, Google, Ollama,
  Gemma, OMS, Manual MSD ou pelos autores dos documentos da base.
- Documentos recuperados servem somente como fontes de conteúdo sobre saúde
  mental e jamais indicam quem criou ou desenvolveu você.

REGRAS OBRIGATÓRIAS:

1. Responda sempre em português do Brasil.

2. Seja acolhedora, respeitosa, clara, objetiva e fácil de entender.

3. Não faça diagnósticos médicos ou psicológicos.

4. Não afirme que o usuário possui um transtorno, doença ou condição.

5. Não prescreva medicamentos, doses, tratamentos ou alterações
   em tratamentos existentes.

6. Não invente informações, definições, fontes, páginas,
   sintomas, números ou critérios clínicos.

7. Quando houver contexto documental, utilize exclusivamente
   as informações presentes nesse contexto.

8. Não complete siglas ou nomes utilizando conhecimento próprio.
   Utilize apenas definições explicitamente presentes no contexto.

9. Não diga que determinado sintoma pertence a um transtorno
   quando essa relação não estiver claramente descrita no contexto.

10. Não transforme critérios clínicos em diagnóstico do usuário.

11. Ao mencionar critérios diagnósticos, deixe claro que:
    - são informações educativas;
    - são utilizados como referência por profissionais;
    - não permitem concluir um diagnóstico por esta conversa.

12. Nunca use expressões como:
    - "isso confirma o diagnóstico";
    - "para confirmar o diagnóstico";
    - "você tem";
    - "você sofre de";
    - "seus sintomas indicam";
    - "isso significa que você possui".

13. Prefira expressões como:
    - "o documento descreve";
    - "entre os critérios avaliados por profissionais";
    - "essa informação é educativa";
    - "somente uma avaliação profissional pode investigar o caso".

14. Caso nenhum documento relevante seja encontrado, informe
    claramente que a base documental não possui informações
    suficientes para responder com segurança.

15. Quando o contexto não responder diretamente à pergunta,
    não complete a resposta utilizando conhecimento geral.

16. Não apresente como fato uma informação que o documento
    apenas menciona superficialmente.

17. Saudações, agradecimentos e despedidas simples não precisam
    utilizar documentos.

18. Não suponha que o usuário está em sofrimento apenas porque
    fez uma pergunta sobre saúde mental.

19. Quando a mensagem indicar sofrimento emocional, incentive
    a busca por apoio profissional de forma cuidadosa,
    sem alarmismo.

20. Em situações explícitas de risco imediato, perigo,
    tentativa de suicídio ou intenção de se machucar,
    oriente a procurar imediatamente um serviço de emergência
    e ajuda de uma pessoa de confiança.

21. Nunca utilize informações do contexto que não tenham relação
    direta com a pergunta do usuário.

22. Não mencione medicamentos ou doses, a menos que o usuário
    tenha feito uma pergunta diretamente relacionada e o contexto
    documental apresente essa informação de forma relevante.
23. Escreva como uma conversa natural entre duas pessoas.

24. Não comece repetidamente com expressões como:
    - "O documento informa";
    - "O documento descreve";
    - "Com base nos documentos fornecidos";
    - "De acordo com o trecho documental".

25. Apresente primeiro a resposta de maneira natural e acolhedora.

26. Quando precisar citar a fonte, coloque-a de forma discreta
    ao final da informação, entre parênteses.

27. Não mencione números de trechos, chunks ou expressões como
    "trecho 0" e "trecho 1" na resposta ao usuário.

28. Em mensagens de sofrimento pessoal, priorize acolhimento,
    segurança e ações práticas antes de informações educativas.

29. Quando o usuário disser "explique melhor", "detalhe",
    "aprofunde", "continue" ou "fale mais", entenda que ele se
    refere ao último assunto da conversa.

30. Nesses pedidos de continuação, não repita a resposta anterior.
    Acrescente novos detalhes relevantes, organize a explicação de
    outra forma e use exemplos simples apenas quando forem compatíveis
    com o contexto documental.

31. Não comece a resposta com prefixos como "Zophia:",
    "Assistente:" ou "Resposta:".

32. Evite dizer "o documento descreve" ou "de acordo com os
    documentos". Explique naturalmente e cite a fonte apenas ao final.
""".strip()


HEALTH_TERMS = {
    # Termos gerais
    "saude mental",
    "mental",
    "emocional",
    "emocao",
    "emocoes",
    "sentimento",
    "sentimentos",
    "psicologico",
    "psicologica",
    "psicologia",
    "psiquiatria",
    "psiquiatra",
    "psicologo",
    "psicologa",
    "terapia",
    "psicoterapia",
    "terapeuta",

    # Ansiedade
    "ansiedade",
    "ansioso",
    "ansiosa",
    "preocupacao",
    "preocupado",
    "preocupada",
    "nervoso",
    "nervosa",
    "medo",
    "panico",
    "ataque de panico",

    # Depressão e humor
    "depressao",
    "depressivo",
    "depressiva",
    "tristeza",
    "triste",
    "desanimo",
    "desanimado",
    "desanimada",
    "humor",
    "bipolaridade",
    "bipolar",
    "mania",

    # Estresse
    "estresse",
    "estressado",
    "estressada",
    "burnout",
    "esgotamento",
    "cansaco",
    "cansado",
    "cansada",

    # Sono
    "insonia",
    "sono",
    "dormir",
    "pesadelo",
    "pesadelos",

    # Sintomas e comportamentos
    "sintoma",
    "sintomas",
    "transtorno",
    "transtornos",
    "crise",
    "crises",
    "trauma",
    "traumatico",
    "traumatica",
    "toc",
    "compulsao",
    "obsessao",
    "tdah",
    "autismo",
    "tea",
    "psicose",
    "alucinacao",
    "delirio",

    # Ajuda e acolhimento
    "ajuda",
    "apoio",
    "acolhimento",
    "desabafar",
    "conversar",
    "sofrimento",
    "sofrendo",
    "mal emocionalmente",

    # Segurança
    "suicidio",
    "suicida",
    "morrer",
    "me matar",
    "tirar minha vida",
    "nao quero viver",
    "automutilacao",
    "autolesao",
    "me machucar",

    # Tratamento
    "tratamento",
    "medicamento",
    "remedio",
    "antidepressivo",
    "ansiolitico",
    "diagnostico",
    "avaliacao profissional",
}


GENERAL_LLM_REQUESTS = {
    "puxe na sua llm",
    "puxa na sua llm",
    "use sua llm",
    "use a sua llm",
    "use seu conhecimento",
    "use o seu conhecimento",
    "responda com seu conhecimento",
    "responda pelo seu conhecimento",
    "responda sem os documentos",
    "nao use os documentos",
    "nao use o rag",
    "fora da base",
    "procure na sua inteligencia",
    "use sua inteligencia",
    "pergunte para sua llm",
}


VAGUE_MESSAGES = {
    "isso",
    "aquilo",
    "continue",
    "continua",
    "continue falando",
    "fale mais",
    "explique melhor",
    "como assim",
    "por que",
    "porque",
    "e agora",
    "e isso",
    "puxe isso",
    "pesquise isso",
    "use isso",
    "responda isso",
    "me diga mais",
    "quero saber mais",
}


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


def _extract_result_value(
    result: Any,
    possible_keys: list[str],
    default: Any = None,
) -> Any:
    """
    Recupera valores de resultados retornados pelo RAG,
    aceitando diferentes formatos.
    """

    if isinstance(result, dict):
        for key in possible_keys:
            if key in result:
                return result[key]

    for key in possible_keys:
        if hasattr(result, key):
            return getattr(result, key)

    return default


def _build_document_context(
    rag_results: Any,
) -> str:
    """
    Converte os resultados do RAG em contexto textual
    organizado para a LLM.
    """

    if not rag_results:
        return ""

    formatted_chunks: list[str] = []

    if isinstance(rag_results, dict):
        if "results" in rag_results:
            rag_results = rag_results["results"]

        elif "documents" in rag_results:
            documents = rag_results.get(
                "documents",
                [],
            )

            metadatas = rag_results.get(
                "metadatas",
                [],
            )

            distances = rag_results.get(
                "distances",
                [],
            )

            if (
                documents
                and isinstance(documents[0], list)
            ):
                documents = documents[0]

            if (
                metadatas
                and isinstance(metadatas[0], list)
            ):
                metadatas = metadatas[0]

            if (
                distances
                and isinstance(distances[0], list)
            ):
                distances = distances[0]

            for index, document in enumerate(documents):
                if not isinstance(document, str):
                    continue

                document = document.strip()

                if not document:
                    continue

                metadata = (
                    metadatas[index]
                    if (
                        index < len(metadatas)
                        and isinstance(
                            metadatas[index],
                            dict,
                        )
                    )
                    else {}
                )

                source = metadata.get(
                    "source",
                    metadata.get(
                        "filename",
                        "Documento não informado",
                    ),
                )

                page = metadata.get(
                    "page",
                    metadata.get(
                        "page_number",
                        "não informada",
                    ),
                )

                chunk = metadata.get(
                    "chunk",
                    metadata.get(
                        "chunk_index",
                        "não informado",
                    ),
                )

                formatted_chunks.append(
                    f"[TRECHO DOCUMENTAL {index + 1}]\n"
                    f"Documento: {source}\n"
                    f"Página: {page}\n"
                    f"Trecho identificado: {chunk}\n"
                    f"Conteúdo:\n{document}"
                )

            return "\n\n---\n\n".join(
                formatted_chunks
            )

    if not isinstance(rag_results, list):
        return ""

    for index, result in enumerate(
        rag_results,
        start=1,
    ):
        document = _extract_result_value(
            result,
            [
                "document",
                "content",
                "text",
                "chunk",
            ],
            "",
        )

        if not isinstance(document, str):
            continue

        document = document.strip()

        if not document:
            continue

        metadata = _extract_result_value(
            result,
            ["metadata"],
            {},
        ) or {}

        source = _extract_result_value(
            result,
            ["source", "filename"],
            None,
        )

        page = _extract_result_value(
            result,
            ["page", "page_number"],
            None,
        )

        chunk = _extract_result_value(
            result,
            ["chunk_index"],
            None,
        )

        if isinstance(metadata, dict):
            source = source or metadata.get(
                "source",
                metadata.get("filename"),
            )

            if page is None:
                page = metadata.get(
                    "page",
                    metadata.get("page_number"),
                )

            if chunk is None:
                chunk = metadata.get(
                    "chunk",
                    metadata.get("chunk_index"),
                )

        source = (
            source
            or "Documento não informado"
        )

        page = (
            page
            if page is not None
            else "não informada"
        )

        chunk = (
            chunk
            if chunk is not None
            else "não informado"
        )

        formatted_chunks.append(
            f"[TRECHO DOCUMENTAL {index}]\n"
            f"Documento: {source}\n"
            f"Página: {page}\n"
            f"Trecho identificado: {chunk}\n"
            f"Conteúdo:\n{document}"
        )

    return "\n\n---\n\n".join(
        formatted_chunks
    )


def _build_user_prompt(
    question: str,
    document_context: str,
    conversation_history: str,
) -> str:
    """
    Monta o prompt usando o histórico completo, a pergunta atual
    e as informações recuperadas pelo RAG.
    """

    continuation_instructions = """
PEDIDOS DE CONTINUAÇÃO:
Se a mensagem atual for algo como "explique melhor", "detalhe",
"aprofunde", "continue" ou "fale mais":

- identifique o último assunto usando o histórico;
- considere também a resposta anterior da assistente;
- não repita a mesma definição ou os mesmos critérios;
- acrescente detalhes novos e relevantes;
- explique de maneira mais simples e organizada;
- use exemplos cotidianos somente quando forem sustentados pelo contexto;
- se não houver informação nova suficiente, diga isso claramente.
""".strip()

    if not document_context:
        return f"""
HISTÓRICO RECENTE DA CONVERSA:
{conversation_history or "Nenhum histórico anterior."}

MENSAGEM ATUAL DO USUÁRIO:
{question}

RESULTADO DA CONSULTA DOCUMENTAL:
Nenhum trecho suficientemente relevante foi encontrado.

{continuation_instructions}

INSTRUÇÕES:

- Use o histórico para compreender referências e continuações.
- Não invente informações clínicas ou use conhecimento externo.
- Se for possível responder apenas de forma conversacional, responda
  naturalmente.
- Se a resposta exigir informação clínica ausente, informe que a base
  documental não contém dados suficientes.
- Não mencione RAG, banco vetorial, chunks, busca ou contexto interno.
- Fale de forma humana, acolhedora, clara e direta.
- Não inicie com "Zophia:", "Assistente:" ou "Resposta:".
""".strip()

    return f"""
HISTÓRICO RECENTE DA CONVERSA:
{conversation_history or "Nenhum histórico anterior."}

MENSAGEM ATUAL DO USUÁRIO:
{question}

INFORMAÇÕES DE APOIO RECUPERADAS:
{document_context}

{continuation_instructions}

TAREFA:
Responda à mensagem atual considerando o histórico completo e usando
somente as informações clínicas relevantes recuperadas.

REGRAS OBRIGATÓRIAS:

- Use o histórico para entender a intenção e o assunto da mensagem atual.
- Considere a resposta anterior para evitar repetição.
- Responda como em uma conversa natural entre duas pessoas.
- Apresente diretamente a explicação; não trate a resposta como análise
  de documentos.
- Não comece com "o documento informa", "o documento descreve",
  "com base nos documentos" ou expressão equivalente.
- Não mencione banco vetorial, RAG, chunks ou trechos recuperados.
- Ignore qualquer informação que não responda diretamente à pergunta.
- Não invente sintomas, causas, tratamentos, diagnósticos ou estatísticas.
- Não afirme que o usuário possui um transtorno.
- Não prescreva medicamentos nem informe doses.
- Quando necessário, cite a fonte discretamente ao final no formato:
  (Fonte: nome do documento, página X).
- Não repita a mesma fonte em todos os parágrafos.
- Se houver critérios diagnósticos, apresente-os como informação educativa
  usada por profissionais, sem concluir diagnóstico.
- Priorize acolhimento quando houver relato pessoal.
- Não inicie com "Zophia:", "Assistente:" ou "Resposta:".
""".strip()


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


# Compatibilidade com nomes utilizados
# em outras partes do projeto.
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