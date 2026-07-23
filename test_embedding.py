import asyncio

from backend.services.embedding_service import generate_embedding


async def main():
    embedding = await generate_embedding(
        "Estou me sentindo muito ansioso."
    )

    print("Embedding gerado com sucesso.")
    print("Quantidade de números:", len(embedding))
    print("Primeiros valores:", embedding[:5])


if __name__ == "__main__":
    asyncio.run(main())