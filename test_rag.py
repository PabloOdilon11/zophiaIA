from pathlib import Path
import hashlib


PASTA = Path("backend/knowledge/documentos")


def calcular_hash(caminho):
    hash_sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(8192), b""):
            hash_sha256.update(bloco)

    return hash_sha256.hexdigest()


for nome in ["anxiety.pdf", "depression.pdf", "mhgap.pdf"]:
    caminho = PASTA / nome

    if not caminho.exists():
        print(f"{nome}: arquivo não encontrado")
        continue

    print(f"{nome}")
    print(f"Tamanho: {caminho.stat().st_size} bytes")
    print(f"SHA256: {calcular_hash(caminho)}")
    print("-" * 70)