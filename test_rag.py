import asyncio

from backend.services.rag_service import search_documents


async def main():
    result = await search_documents(
        "Quais são os sintomas da depressão?"
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        print(f"\n===== Resultado {i+1} =====")
        print(f"Distância: {dist:.4f}")
        print(f"Arquivo: {meta['source']}")
        print(f"Página: {meta['page']}")
        print(doc[:500])


asyncio.run(main())