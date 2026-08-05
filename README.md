# 🧠 Zophia Lite

Assistente virtual educativa para apoio em saúde mental, utilizando *Large Language Models*, Recuperação Aumentada por Geração (RAG), embeddings e banco vetorial.

---

## 📖 Sobre o projeto

A Zophia Lite é uma aplicação web conversacional desenvolvida como projeto acadêmico por estudantes do curso de Ciência da Computação da Universidade Estadual da Paraíba (UEPB).

Seu objetivo é oferecer informações educativas sobre saúde mental de forma clara, acolhedora e responsável. A aplicação combina uma interface em React, uma API em FastAPI, o modelo Gemma 3 4B executado localmente pelo Ollama, ChromaDB, embeddings e um pipeline RAG.

> ⚠️ A Zophia Lite **não substitui** psicólogos, psiquiatras, médicos ou serviços de emergência.

---

## 🎯 Objetivos

- Fornecer informações educativas sobre saúde mental.
- Recuperar conteúdos relevantes de documentos especializados.
- Reduzir respostas genéricas e fora de contexto.
- Manter memória da conversa.
- Separar perguntas gerais de perguntas relacionadas à saúde mental.
- Detectar mensagens críticas e oferecer orientações iniciais de segurança.

---

## ✨ Principais funcionalidades

- Chat conversacional.
- Roteamento inteligente de intenções.
- Memória conversacional.
- Busca semântica por embeddings.
- Recuperação de documentos com RAG.
- Respostas fundamentadas com referência ao documento.
- Perguntas gerais sem consulta ao banco vetorial.
- Respostas locais para data, hora, saudação e identidade.
- Tratamento inicial de mensagens de crise.
- Execução local do modelo por meio do Ollama.

---

## 🏗️ Arquitetura

<p align="center">
  <img src="docs/arquitetura_zophia.png" alt="Arquitetura da Zophia Lite" width="900">
</p>

**Fluxo principal:**

```text
React
  ↓
FastAPI
  ↓
router.py
  ├── respostas locais
  ├── memória
  ├── perguntas gerais
  ├── fluxo de crise
  └── saúde mental
          ↓
       Pipeline RAG
          ↓
      Embeddings
          ↓
       ChromaDB
          ↓
         PDFs
          ↓
    Gemma 3 4B / Ollama
          ↓
     Resposta ao usuário
```

---

## 🧩 Principais módulos

### `router.py`

Classifica a intenção da mensagem antes de qualquer consulta ao modelo ou ao RAG.

Exemplos de intenções:

```text
GREETING
DATETIME
ABOUT_ZOPHIA
MEMORY
GENERAL
MENTAL_HEALTH
CONTEXT_FOLLOW_UP
CRISIS
```

### `llm_service.py`

Coordena o fluxo de resposta. Recebe a intenção classificada pelo roteador e encaminha a mensagem para o serviço apropriado.

### `rag_service.py`

Executa a busca semântica na base vetorial e recupera os trechos mais relevantes dos documentos.

### `embedding_service.py`

Transforma perguntas e trechos dos documentos em vetores numéricos.

### `conversation_service.py`

Mantém o histórico recente da conversa e o identificador da sessão.

### `crisis_service.py`

Fornece respostas determinísticas para mensagens explícitas de risco, sem depender da geração livre do modelo.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia          | Finalidade                          |
| ------------------- | ----------------------------------- |
| React               | Interface web                       |
| FastAPI             | API e backend                       |
| Python              | Serviços e regras de negócio        |
| JavaScript          | Desenvolvimento do frontend         |
| Ollama              | Execução local dos modelos          |
| Gemma 3 4B          | Geração das respostas               |
| nomic-embed-text    | Geração de embeddings               |
| ChromaDB            | Banco de dados vetorial             |
| RAG                 | Recuperação de contexto documental  |
| Git e GitHub        | Versionamento do projeto            |

---

## 📂 Estrutura do projeto

```text
zophiaIA/
├── backend/
│   ├── routes/
│   ├── services/
│   ├── knowledge/
│   ├── vector_db/
│   └── main.py
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── docs/
│   ├── arquitetura_zophia.png
│   ├── Relatorio_Tecnico.pdf
│   └── Manual_Instalacao.pdf
├── tests/
│   └── test_cases.md
├── executavel/
│   ├── Windows/
│   └── MacOS/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Pré-requisitos

- Python 3.11 ou superior.
- Node.js LTS.
- npm.
- Ollama.
- Git.

---

## 📥 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/PabloOdilon11/zophiaIA.git
cd zophiaIA
git checkout new-frontend
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

**Windows:**

```powershell
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Instalar as dependências do backend

```bash
pip install -r requirements.txt
```

### 4. Instalar as dependências do frontend

```bash
cd frontend
npm install
cd ..
```

### 5. Baixar os modelos do Ollama

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

---

## ▶️ Execução

### Backend

Na raiz do projeto:

```bash
python -m uvicorn backend.main:app --reload
```

- Backend disponível em: `http://127.0.0.1:8000`
- Documentação Swagger: `http://127.0.0.1:8000/docs`

### Frontend

Em outro terminal:

```bash
cd frontend
npm run dev
```

- Frontend disponível em: `http://127.0.0.1:5173`

---

## 📚 Base documental

A base utilizada pelo pipeline RAG inclui documentos como:

- `anxiety.pdf`
- `mhgap.pdf`
- `cartilha_cvv.pdf`

Os documentos são divididos em trechos, transformados em embeddings e armazenados no ChromaDB.

---

## 🧪 Testes

Os testes funcionais verificam:

| Caso | Entrada                      | Intenção esperada   |
| ---- | ---------------------------- | ------------------- |
| T01  | Oi                           | GREETING            |
| T02  | Que dia é hoje?              | DATETIME            |
| T03  | Quem criou você?             | ABOUT_ZOPHIA        |
| T04  | Quanto é 2 + 2?              | GENERAL             |
| T05  | O que é ansiedade?           | MENTAL_HEALTH       |
| T06  | Explique melhor              | CONTEXT_FOLLOW_UP   |
| T07  | O que eu perguntei antes?    | MEMORY              |
| T08  | Mensagem explícita de risco  | CRISIS              |

Os casos completos estão disponíveis em: `tests/test_cases.md`

---

## ⚠️ Limitações

- O histórico é armazenado apenas durante a execução do backend.
- A aplicação depende do Ollama instalado localmente.
- O desempenho varia conforme o hardware.
- A base documental ainda é limitada.
- O fluxo de crise não substitui atendimento profissional.
- A aplicação ainda não está hospedada publicamente.

---

## 🔮 Trabalhos futuros

- Persistência das conversas em banco de dados.
- Máquina de estados completa para o fluxo de crise.
- Hospedagem em nuvem.
- Autenticação de usuários.
- Painel administrativo.
- Ampliação da base documental.
- Avaliações automáticas de relevância do RAG.
- Aplicativo para dispositivos móveis.
- Recursos adicionais de acessibilidade.

---

## 📄 Documentação

- Relatório técnico: [`docs/Relatorio_Tecnico.pdf`](docs/Relatorio_Tecnico.pdf)
- Manual de instalação: [`docs/Manual_Instalacao.pdf`](docs/Manual_Instalacao.pdf)
- Casos de teste: [`tests/test_cases.md`](tests/test_cases.md)
- Vídeo demonstrativo: *adicionar link após a publicação.*

---

## 👨‍💻 Autores

- Pablo Odilon Agra de Queiroz
- Luiz José Mendonça Duarte
- Kaio Emanuel Rosemiro de Carvalho
- Deyvid Jerônimo de Araújo Macêdo

**Universidade Estadual da Paraíba — UEPB**
Curso de Ciência da Computação
Disciplina: Tópicos Especiais em Computação

---

## 📜 Licença

Projeto desenvolvido para fins acadêmicos e educacionais.
