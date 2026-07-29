import os
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

# Validação dos resultados recuperados pelo ChromaDB.
# Em distância cosseno, valores menores indicam maior proximidade.
MAX_RAG_DISTANCE = float(os.getenv("MAX_RAG_DISTANCE", "0.75"))
MIN_DOCUMENT_CHARS = int(os.getenv("MIN_DOCUMENT_CHARS", "60"))
MAX_VALID_CHUNKS = int(os.getenv("MAX_VALID_CHUNKS", "3"))


SYSTEM_PROMPT = """
Você é a Zophia, uma assistente virtual educativa de apoio à saúde mental.

Sua função é oferecer informações educativas e acolhimento inicial.
Você não substitui psicólogos, psiquiatras, médicos ou serviços
de emergência.

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


def _normalize_document_for_deduplication(document: str) -> str:
    """Normaliza um trecho para detectar resultados repetidos."""

    return " ".join(_normalize_message(document).split())


def _is_valid_distance(distance: Any) -> bool:
    """
    Valida a distância retornada pelo ChromaDB. Quando a distância não
    é fornecida, o trecho pode continuar no fluxo por compatibilidade.
    """

    if distance is None:
        return True

    try:
        numeric_distance = float(distance)
    except (TypeError, ValueError):
        return False

    return 0.0 <= numeric_distance <= MAX_RAG_DISTANCE


def _build_validated_chunk(
    document: Any,
    metadata: Any,
    distance: Any,
    seen_documents: set[str],
) -> dict[str, Any] | None:
    """Valida conteúdo, relevância, metadados e duplicidade do trecho."""

    if not isinstance(document, str):
        return None

    document = document.strip()

    if len(document) < MIN_DOCUMENT_CHARS:
        return None

    if not _is_valid_distance(distance):
        return None

    if not isinstance(metadata, dict):
        metadata = {}

    source = metadata.get("source") or metadata.get("filename")

    # Uma fonte sem identificação não pode ser apresentada como confiável.
    if not isinstance(source, str) or not source.strip():
        return None

    normalized_document = _normalize_document_for_deduplication(document)

    if not normalized_document or normalized_document in seen_documents:
        return None

    seen_documents.add(normalized_document)

    page = metadata.get("page", metadata.get("page_number"))
    chunk = metadata.get("chunk", metadata.get("chunk_index"))

    return {
        "document": document,
        "source": source.strip(),
        "page": page if page is not None else "não informada",
        "chunk": chunk if chunk is not None else "não informado",
        "distance": distance,
    }


def _build_document_context(
    rag_results: Any,
) -> str:
    """
    Valida os resultados recuperados e converte somente os trechos
    confiáveis e relevantes em contexto para a LLM.
    """

    if not rag_results:
        return ""

    validated_chunks: list[dict[str, Any]] = []
    seen_documents: set[str] = set()
    total_candidates = 0

    if isinstance(rag_results, dict) and "results" in rag_results:
        rag_results = rag_results["results"]

    if isinstance(rag_results, dict) and "documents" in rag_results:
        documents = rag_results.get("documents", [])
        metadatas = rag_results.get("metadatas", [])
        distances = rag_results.get("distances", [])

        if documents and isinstance(documents[0], list):
            documents = documents[0]

        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]

        if distances and isinstance(distances[0], list):
            distances = distances[0]

        total_candidates = len(documents)

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

            validated = _build_validated_chunk(
                document=document,
                metadata=metadata,
                distance=distance,
                seen_documents=seen_documents,
            )

            if validated is not None:
                validated_chunks.append(validated)

            if len(validated_chunks) >= MAX_VALID_CHUNKS:
                break

    elif isinstance(rag_results, list):
        total_candidates = len(rag_results)

        for result in rag_results:
            document = _extract_result_value(
                result,
                ["document", "content", "text", "chunk"],
                "",
            )
            metadata = _extract_result_value(
                result,
                ["metadata"],
                {},
            ) or {}

            if not isinstance(metadata, dict):
                metadata = {}

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
            distance = _extract_result_value(
                result,
                ["distance"],
                None,
            )

            if source is not None:
                metadata.setdefault("source", source)
            if page is not None:
                metadata.setdefault("page", page)
            if chunk is not None:
                metadata.setdefault("chunk", chunk)

            validated = _build_validated_chunk(
                document=document,
                metadata=metadata,
                distance=distance,
                seen_documents=seen_documents,
            )

            if validated is not None:
                validated_chunks.append(validated)

            if len(validated_chunks) >= MAX_VALID_CHUNKS:
                break

    print(
        "[RAG VALIDATION] "
        f"recebidos={total_candidates} | "
        f"aceitos={len(validated_chunks)} | "
        f"limite_distancia={MAX_RAG_DISTANCE}"
    )

    formatted_chunks: list[str] = []

    for index, chunk_data in enumerate(validated_chunks, start=1):
        formatted_chunks.append(
            f"[TRECHO DOCUMENTAL {index}]\n"
            f"Documento: {chunk_data['source']}\n"
            f"Página: {chunk_data['page']}\n"
            f"Trecho identificado: {chunk_data['chunk']}\n"
            f"Conteúdo:\n{chunk_data['document']}"
        )

    return "\n\n---\n\n".join(formatted_chunks)

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
    *,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """
    Envia o prompt para o Gemma 3 pelo Ollama.
    """

    full_prompt = (
        f"{system_prompt}\n\n"
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
        

GENERAL_SYSTEM_PROMPT = """
Você é a Zophia, uma assistente virtual educativa.

Responda sempre em português do Brasil, de forma clara, objetiva e natural.
Para perguntas gerais, use seu conhecimento normalmente, sem mencionar documentos,
RAG, banco vetorial ou contexto interno.

Não invente fatos quando não souber. Em temas médicos, psicológicos, jurídicos ou
financeiros, deixe claras as limitações e evite diagnósticos, prescrições ou garantias.
Não comece a resposta com "Zophia:", "Assistente:" ou "Resposta:".
""".strip()


def _build_general_prompt(
    question: str,
    conversation_history: str,
) -> str:
    return f"""
HISTÓRICO RECENTE DA CONVERSA:
{conversation_history or "Nenhum histórico anterior."}

MENSAGEM ATUAL DO USUÁRIO:
{question}

Responda diretamente à mensagem atual. Use o histórico somente quando ele for
necessário para entender referências ou dar continuidade ao assunto.
""".strip()


def _datetime_response(message: str) -> str:
    normalized = _normalize_message(message)
    now = datetime.now()

    weekdays = (
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    )

    months = (
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    )

    if "hora" in normalized or "horario" in normalized:
        return f"Agora são {now:%H:%M}."

    if "mes" in normalized:
        return f"Estamos em {months[now.month - 1]} de {now.year}."

    if "ano" in normalized:
        return f"Estamos no ano de {now.year}."

    return (
        f"Hoje é {weekdays[now.weekday()]}, "
        f"{now.day} de {months[now.month - 1]} de {now.year}."
    )


def _memory_response(
    question: str,
    conversation_id: str,
) -> str:
    normalized = _normalize_message(question)
    messages = conversation_manager.get_messages(conversation_id)

    previous_messages = messages[:-1] if messages else []
    user_messages = [
        message.content
        for message in previous_messages
        if message.role == "user"
    ]
    assistant_messages = [
        message.content
        for message in previous_messages
        if message.role == "assistant"
    ]

    if not user_messages and not assistant_messages:
        return "Ainda não há mensagens anteriores nesta conversa."

    if "primeira" in normalized or "primeiro" in normalized:
        if user_messages:
            return f'Sua primeira mensagem foi: "{user_messages[0]}"'
        return "Ainda não encontrei uma mensagem anterior sua nesta conversa."

    if (
        "ultima mensagem" in normalized
        or "mensagem anterior" in normalized
        or "perguntei antes" in normalized
        or "falei antes" in normalized
        or "disse antes" in normalized
    ):
        if user_messages:
            return f'Sua mensagem anterior foi: "{user_messages[-1]}"'
        return "Ainda não encontrei uma mensagem anterior sua nesta conversa."

    if "o que voce respondeu" in normalized:
        if assistant_messages:
            return f'Minha resposta anterior foi: "{assistant_messages[-1]}"'
        return "Ainda não há uma resposta anterior minha nesta conversa."

    history = conversation_manager.build_history(
        conversation_id=conversation_id,
        exclude_last_user_message=True,
    )

    prompt = f"""
HISTÓRICO DA CONVERSA:
{history}

PERGUNTA SOBRE O HISTÓRICO:
{question}

Responda usando somente o histórico apresentado. Não acrescente informações que
não estejam nele. Seja breve e não mencione RAG ou documentos.
""".strip()

    return _call_ollama(
        prompt,
        system_prompt=GENERAL_SYSTEM_PROMPT,
    )


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
    """
    Gera uma resposta, mantém o histórico e direciona a mensagem
    para o serviço correto por meio do roteador de intenções.
    """

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

    previous_messages = conversation_manager.get_messages(
        current_conversation_id
    )
    has_conversation_history = bool(previous_messages)
    crisis_active = conversation_manager.is_crisis_active(
        current_conversation_id
    )

    conversation_manager.add_message(
        conversation_id=current_conversation_id,
        role="user",
        content=question,
    )

    route = route_message(
        question,
        has_conversation_history=has_conversation_history,
        crisis_active=crisis_active,
    )

    print(
        "[ROUTER] "
        f"intent={route.intent.value} | "
        f"reason={route.reason}"
    )

    if route.intent == Intent.CRISIS:
        if crisis_active:
            response = _crisis_continuation_response(question)
        else:
            conversation_manager.set_crisis_active(
                current_conversation_id,
                True,
            )
            response = _crisis_response()

    elif route.intent == Intent.GREETING:
        response = _greeting_response(question)

    elif route.intent == Intent.THANKS:
        response = _thanks_response()

    elif route.intent == Intent.GOODBYE:
        response = _goodbye_response()

    elif route.intent == Intent.MEMORY:
        response = _memory_response(
            question=question,
            conversation_id=current_conversation_id,
        )

    elif route.intent == Intent.DATETIME:
        response = _datetime_response(question)

    elif route.intent == Intent.GENERAL:
        conversation_history = conversation_manager.build_history(
            conversation_id=current_conversation_id,
            exclude_last_user_message=True,
        )
        general_prompt = _build_general_prompt(
            question=question,
            conversation_history=conversation_history,
        )
        response = _call_ollama(
            general_prompt,
            system_prompt=GENERAL_SYSTEM_PROMPT,
        )

    else:
        # MENTAL_HEALTH e CONTEXT_FOLLOW_UP consultam o RAG.
        conversation_history = conversation_manager.build_history(
            conversation_id=current_conversation_id,
            exclude_last_user_message=True,
        )

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
            conversation_history=conversation_history,
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