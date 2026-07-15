# Análise das Tecnologias Utilizadas

## Objetivo

O desenvolvimento do Zophia Lite requer tecnologias que permitam construir uma aplicação modular, escalável e de fácil manutenção.

Nesta primeira etapa foram selecionadas as ferramentas que serão utilizadas durante o restante do projeto.

---

# Tecnologias Selecionadas

## Python

### Finalidade

Python será a linguagem principal do projeto.

### Justificativa

Foi escolhida por possuir:

- ampla utilização em Inteligência Artificial;
- excelente integração com bibliotecas de Machine Learning;
- grande comunidade;
- vasta documentação.

Além disso, praticamente todas as bibliotecas utilizadas no projeto possuem suporte nativo para Python.

---

## Streamlit

### Finalidade

Construção da interface web.

### Justificativa

O Streamlit permite desenvolver interfaces interativas rapidamente utilizando apenas Python.

Vantagens:

- desenvolvimento rápido;
- fácil manutenção;
- integração com IA;
- ideal para protótipos.

---

## Pandas

### Finalidade

Manipulação do dataset.

### Justificativa

Será utilizado para:

- leitura do CSV;
- exploração dos dados;
- filtragem;
- estatísticas;
- seleção de relatos.

---

## Matplotlib

### Finalidade

Visualização dos dados.

### Justificativa

Permite gerar gráficos para análise exploratória, como:

- distribuição das categorias;
- tamanho dos relatos;
- estatísticas gerais.

---

## PyMuPDF

### Finalidade

Leitura dos documentos PDF.

### Justificativa

Será utilizado nas próximas etapas para:

- abrir PDFs;
- extrair texto;
- preservar páginas;
- recuperar metadados.

---

## Sentence Transformers

### Finalidade

Geração de Embeddings.

### Justificativa

Converte textos em vetores semânticos.

Esses vetores serão utilizados pelo mecanismo de busca do RAG.

---

## FAISS

### Finalidade

Banco Vetorial.

### Justificativa

Será responsável por:

- armazenar embeddings;
- executar buscas por similaridade;
- recuperar os documentos mais relevantes.

Foi escolhido por apresentar alto desempenho e ampla utilização em aplicações RAG.

---

## Modelo de Linguagem (LLM)

### Finalidade

Gerar respostas em linguagem natural.

### Justificativa

O modelo receberá:

- relato do usuário;
- documentos recuperados;
- instruções do sistema.

Com essas informações produzirá respostas fundamentadas.

---

## Git

### Finalidade

Controle de versão.

### Justificativa

Permitirá:

- desenvolvimento colaborativo;
- histórico das alterações;
- recuperação de versões anteriores.

---

## GitHub

### Finalidade

Hospedagem do projeto.

### Justificativa

Será utilizado para:

- armazenamento do código;
- documentação;
- organização do projeto;
- colaboração entre os integrantes.

---

# Comparação das Tecnologias

| Tecnologia | Finalidade |
|------------|------------|
| Python | Linguagem principal |
| Streamlit | Interface |
| Pandas | Manipulação do dataset |
| Matplotlib | Gráficos |
| PyMuPDF | Leitura de PDFs |
| Sentence Transformers | Embeddings |
| FAISS | Banco vetorial |
| LLM | Geração das respostas |
| Git | Versionamento |
| GitHub | Repositório |

---

# Justificativa Geral

As tecnologias escolhidas apresentam boa integração entre si, possuem ampla documentação e são amplamente utilizadas em aplicações modernas de Inteligência Artificial.

Além disso, permitem que o sistema evolua de forma incremental, atendendo aos requisitos de cada etapa do projeto.

Na Semana 1 serão utilizados principalmente:

- Python;
- Pandas;
- Matplotlib;
- Streamlit;
- Git;
- GitHub.

As demais tecnologias serão incorporadas nas próximas semanas durante a implementação do pipeline RAG.