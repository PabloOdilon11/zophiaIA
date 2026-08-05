"""Formatação dos resultados do RAG e construção do prompt do usuário."""

from typing import Any

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

