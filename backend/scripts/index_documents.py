import asyncio
import hashlib
import re
from pathlib import Path
from typing import List

from pypdf import PdfReader

from backend.services.embedding_service import generate_embedding
from backend.services.rag_service import collection


DOCUMENTS_PATH = Path("backend/knowledge/documentos")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def clean_text(text: str) -> str:
    """
    Remove espaços e quebras de linha desnecessárias.
    """

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Divide um texto grande em trechos menores.

    Cada trecho possui uma pequena sobreposição com o anterior
    para evitar perda de contexto.
    """

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_chunk_id(
    filename: str,
    page_number: int,
    chunk_number: int,
    text: str,
) -> str:
    """
    Gera um identificador único para cada trecho.
    """

    raw_id = (
        f"{filename}-"
        f"{page_number}-"
        f"{chunk_number}-"
        f"{text}"
    )

    return hashlib.sha256(
        raw_id.encode("utf-8")
    ).hexdigest()


async def index_pdf(pdf_path: Path) -> int:
    """
    Lê um PDF, divide o conteúdo e salva no ChromaDB.
    """

    print(f"\nLendo: {pdf_path.name}")

    reader = PdfReader(str(pdf_path))

    indexed_chunks = 0

    for page_index, page in enumerate(reader.pages):
        page_number = page_index + 1

        extracted_text = page.extract_text() or ""

        text = clean_text(extracted_text)

        if not text:
            print(
                f"Página {page_number}: nenhum texto encontrado."
            )
            continue

        chunks = split_text(text)

        for chunk_index, chunk in enumerate(chunks):
            embedding = await generate_embedding(chunk)

            chunk_id = create_chunk_id(
                filename=pdf_path.name,
                page_number=page_number,
                chunk_number=chunk_index,
                text=chunk,
            )

            collection.upsert(
                ids=[chunk_id],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[
                    {
                        "source": pdf_path.name,
                        "page": page_number,
                        "chunk": chunk_index,
                    }
                ],
            )

            indexed_chunks += 1

            print(
                f"Página {page_number} | "
                f"trecho {chunk_index + 1}/{len(chunks)}"
            )

    return indexed_chunks


async def main():
    """
    Procura todos os PDFs e realiza a indexação.
    """

    if not DOCUMENTS_PATH.exists():
        DOCUMENTS_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            "A pasta de documentos foi criada em:\n"
            f"{DOCUMENTS_PATH.resolve()}"
        )

        print(
            "\nColoque os PDFs nela e execute novamente."
        )

        return

    pdf_files = list(
        DOCUMENTS_PATH.glob("*.pdf")
    )

    if not pdf_files:
        print(
            "Nenhum PDF encontrado em:\n"
            f"{DOCUMENTS_PATH.resolve()}"
        )

        return

    total_chunks = 0

    for pdf_path in pdf_files:
        try:
            total = await index_pdf(pdf_path)

            total_chunks += total

        except Exception as error:
            print(
                f"\nErro ao indexar {pdf_path.name}: {error}"
            )

    print("\nIndexação concluída.")

    print(
        f"Total de trechos armazenados: {total_chunks}"
    )

    print(
        f"Total no banco vetorial: {collection.count()}"
    )


if __name__ == "__main__":
    asyncio.run(main())