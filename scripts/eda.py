from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# ===============================
# Configurações
# ===============================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "dataset" / "mental_health_social_media_posts.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ===============================
    # Carregar Dataset
    # ===============================

    df = pd.read_csv(DATASET_PATH)

    print("=" * 60)
    print("ZOPHIA LITE - EXPLORAÇÃO DO DATASET")
    print("=" * 60)

    # ===============================
    # Informações Gerais
    # ===============================

    print("\nQuantidade de registros:", len(df))
    print("Quantidade de colunas:", len(df.columns))

    print("\nColunas:")
    for col in df.columns:
        print(f"- {col}")

    # ===============================
    # Tipos dos Dados
    # ===============================

    print("\nTipos de Dados")
    print(df.dtypes)

    # ===============================
    # Valores Ausentes
    # ===============================

    print("\nValores Ausentes")
    print(df.isnull().sum())

    # ===============================
    # Duplicados
    # ===============================

    print("\nRegistros Duplicados:", df.duplicated().sum())

    # ===============================
    # Distribuição das Categorias
    # ===============================

    print("\nDistribuição das Categorias")
    categoria = df["tag"].value_counts()
    print(categoria)

    # ===============================
    # Comprimento dos Relatos
    # ===============================

    df["texto_tamanho"] = df["post_content"].str.len()

    print("\nEstatísticas dos Relatos")
    print(df["texto_tamanho"].describe())

    # ===============================
    # Exemplos
    # ===============================

    print("\nExemplos de Relatos")
    for i in range(5):
        print("-" * 40)
        print(df.iloc[i]["tag"])
        print(df.iloc[i]["post_content"])

    # ===============================
    # Gráfico das Categorias
    # ===============================

    plt.figure(figsize=(7, 5))
    categoria.plot(kind="bar")
    plt.title("Distribuição das Categorias")
    plt.xlabel("Categoria")
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "categorias.png")
    plt.close()

    # ===============================
    # Histograma dos Relatos
    # ===============================

    plt.figure(figsize=(7, 5))
    plt.hist(df["texto_tamanho"], bins=20)
    plt.title("Distribuição do Tamanho dos Relatos")
    plt.xlabel("Quantidade de Caracteres")
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "tamanho_relatos.png")
    plt.close()

    # ===============================
    # Relatório Final
    # ===============================

    print("\nResumo")
    print(f"""
Total de registros: {len(df)}

Total de atributos: {len(df.columns) - 1}

Valores ausentes: {df.isnull().sum().sum()}

Categorias:

{categoria}

Tamanho médio dos relatos:
{round(df['texto_tamanho'].mean(), 2)} caracteres

Gráficos salvos em:

outputs/categorias.png
outputs/tamanho_relatos.png
""")

    print("=" * 60)
    print("ANÁLISE FINALIZADA")
    print("=" * 60)


if __name__ == "__main__":
    main()
