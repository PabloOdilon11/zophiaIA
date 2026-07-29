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
DELETE_BATCH_SIZE = 500


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

    if chunk_size <= 0:
        raise ValueError(
            "CHUNK_SIZE deve ser maior que zero."
        )

    if overlap < 0:
        raise ValueError(
            "CHUNK_OVERLAP não pode ser negativo."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "CHUNK_OVERLAP deve ser menor que CHUNK_SIZE."
        )

    chunks: List[str] = []

    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def calculate_file_hash(pdf_path: Path) -> str:
    """
    Calcula o SHA256 do arquivo para identificar PDFs duplicados.
    """

    sha256 = hashlib.sha256()

    with pdf_path.open("rb") as file:
        while True:
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def create_chunk_id(
    file_hash: str,
    page_number: int,
    chunk_number: int,
    text: str,
) -> str:
    """
    Gera um identificador único para cada trecho.
    """

    raw_id = (
        f"{file_hash}-"
        f"{page_number}-"
        f"{chunk_number}-"
        f"{text}"
    )

    return hashlib.sha256(
        raw_id.encode("utf-8")
    ).hexdigest()


def clear_collection() -> None:
    """
    Remove todos os trechos antigos antes de uma nova
    indexação completa.
    """

    total_before = collection.count()

    if total_before == 0:
        print("Banco vetorial já está vazio.")
        return

    print(
        f"\nRemovendo {total_before} trechos antigos..."
    )

    existing_data = collection.get(
        include=[]
    )

    existing_ids = existing_data.get("ids", [])

    for start in range(
        0,
        len(existing_ids),
        DELETE_BATCH_SIZE,
    ):
        batch_ids = existing_ids[
            start:start + DELETE_BATCH_SIZE
        ]

        collection.delete(ids=batch_ids)

    print(
        f"Banco limpo. Total atual: {collection.count()}"
    )


def find_unique_pdfs(
    pdf_files: List[Path],
) -> List[tuple[Path, str]]:
    """
    Detecta PDFs idênticos pelo hash SHA256 e mantém
    somente uma cópia para indexação.
    """

    unique_files: List[tuple[Path, str]] = []
    seen_hashes: dict[str, Path] = {}

    for pdf_path in sorted(pdf_files):
        file_hash = calculate_file_hash(pdf_path)

        duplicate_of = seen_hashes.get(file_hash)

        if duplicate_of is not None:
            print(
                f"\nPDF duplicado ignorado: {pdf_path.name}"
            )
            print(
                f"Conteúdo idêntico a: {duplicate_of.name}"
            )
            continue

        seen_hashes[file_hash] = pdf_path

        unique_files.append(
            (
                pdf_path,
                file_hash,
            )
        )

    return unique_files


async def index_pdf(
    pdf_path: Path,
    file_hash: str,
) -> int:
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
                f"Página {page_number}: "
                "nenhum texto encontrado."
            )
            continue

        chunks = split_text(text)

        for chunk_index, chunk in enumerate(chunks):
            embedding = await generate_embedding(chunk)

            chunk_id = create_chunk_id(
                file_hash=file_hash,
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
                        "file_hash": file_hash,
                    }
                ],
            )

            indexed_chunks += 1

            print(
                f"Página {page_number} | "
                f"trecho {chunk_index + 1}/{len(chunks)}"
            )

    return indexed_chunks


async def main() -> None:
    """
    Limpa o banco, procura os PDFs e realiza
    uma nova indexação completa.
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

    unique_pdfs = find_unique_pdfs(pdf_files)

    if not unique_pdfs:
        print(
            "Nenhum PDF válido foi encontrado para indexação."
        )
        return

    print(
        f"\nPDFs encontrados: {len(pdf_files)}"
    )

    print(
        f"PDFs únicos: {len(unique_pdfs)}"
    )

    clear_collection()

    total_chunks = 0
    failed_files = 0

    for pdf_path, file_hash in unique_pdfs:
        try:
            total = await index_pdf(
                pdf_path=pdf_path,
                file_hash=file_hash,
            )

            total_chunks += total

        except Exception as error:
            failed_files += 1

            print(
                f"\nErro ao indexar "
                f"{pdf_path.name}: {error}"
            )

    print("\nIndexação concluída.")

    print(
        f"Total de trechos armazenados: {total_chunks}"
    )

    print(
        f"Total no banco vetorial: {collection.count()}"
    )

    if failed_files:
        print(
            f"Arquivos que apresentaram erro: {failed_files}"
        )


if __name__ == "__main__":
    asyncio.run(main())