# Zophia - Assistente Inteligente de Apoio à Saúde Mental 💜

## Sobre o Projeto

O **Zophia** é uma aplicação web moderna voltada para o acolhimento, escuta atenta e apoio educacional em saúde mental. 

O sistema combina um **Frontend moderno em React** (estilo ChatGPT/Claude) com um **Backend em Python/FastAPI** embasado na arquitetura **Retrieval-Augmented Generation (RAG)** e documentos científicos de referência.

Este projeto está sendo desenvolvido para a disciplina de Tópicos Especiais em Computação da Universidade Estadual da Paraíba (**UEPB**).

---

## 🚀 Status Atual do Projeto

- **Frontend**: Migrado e reconstruído em **React 18 + Vite + TailwindCSS + Lucide React + Framer Motion**.
- **Backend**: API REST em **FastAPI + Pydantic** integrada ao **Ollama** (`gemma3:4b` e `nomic-embed-text`) e **ChromaDB** para busca semântica RAG.
- **Identidade Visual**: Paleta de cores sólidas oficiais (`#8D3F9E` Roxo, `#ED4F9D` Rosa, `#FCF8F7` Fundo) com tipografia Manrope & DM Sans.
- **UX**: Emotional Check-in de humor, respostas conversacionais com cartões sanfonados expansíveis da estrutura RAG de 7 seções, e modais interativos de *Cuidado Diário*.

---

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18** + **Vite**
- **TailwindCSS**
- **Framer Motion** (animações fluidas)
- **Lucide React** (ícones vetoriais)

### Backend
- **Python 3.10+**
- **FastAPI** + **Uvicorn**
- **Pydantic**
- **ChromaDB** (Banco de dados vetorial)
- **Ollama** (`gemma3:4b` para geração e `nomic-embed-text` para embeddings)
- **Pandas**, **PyMuPDF** & **PyPDF** (processamento de relatos e documentos)

---

## 📁 Estrutura de Diretórios

```
zophiaIA/
├── backend/
│   ├── main.py                # Ponto de entrada FastAPI (CORS, Rotas)
│   ├── models/                # Schemas Pydantic de validação
│   ├── routes/                # Rotas REST (/api/chat, /api/analyze, /api/dataset/stats)
│   ├── scripts/               # Scripts auxiliares (ex: index_documents.py)
│   ├── services/              # Serviços de RAG, Ollama LLM, Embeddings e Análise
│   └── vector_db/             # Banco vetorial local ChromaDB
├── frontend/
│   ├── index.html             # HTML principal com favicon
│   ├── package.json           # Dependências React e Scripts Vite
│   ├── tailwind.config.js     # Configuração de temas e cores sólidas Zophia
│   ├── public/                # Assets e logos estáticas
│   └── src/
│       ├── App.jsx            # Aplicação React principal
│       ├── components/        # Sidebar, Header, ChatMessage, ChatInput, ToolModal, etc.
│       └── styles/            # CSS global e diretivas Tailwind
├── dataset/                   # Relatos utilizados nos testes e análises
├── documents/                 # Base documental RAG (WHO mhGAP, NICE, DSM-5-TR, RAPS, CVV)
└── requirements.txt           # Dependências Python do backend
```

---

## 🛠️ Como Instalar e Rodar o Projeto (Guia Passo a Passo)

### Pré-requisitos Necessários
1. **Node.js** (v18 ou superior)
2. **Python** (v3.10 ou superior)
3. **Ollama** instalado e em execução no sistema.

---

### Passo 1: Pré-requisito do Ollama (LLM & Embeddings)
O backend da Zophia utiliza o Ollama localmente para a geração de respostas e embeddings.

1. Instale o [Ollama](https://ollama.com/) e certifique-se de que ele esteja rodando (ícone do Ollama na barra de tarefas ou serviço ativo).
2. No seu terminal, baixe os modelos necessários:
```bash
ollama pull nomic-embed-text
ollama pull gemma3:4b
```

---

### Passo 2: Clonar o Repositório
```bash
git clone https://github.com/PabloOdilon11/zophiaIA.git
cd zophiaIA
git checkout new-frontend
```

---

### Passo 3: Configurar e Iniciar o Backend (FastAPI)

1. No diretório raiz do projeto (`zophiaIA`), crie e ative um ambiente virtual Python:
```bash
# Criar o ambiente virtual:
python -m venv .venv

# Ativar no Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Ativar no Linux/Mac:
source .venv/bin/activate
```

2. Instale todas as dependências do backend:
```bash
pip install -r requirements.txt
```

3. *(Opcional)* Indexar a base de documentos no ChromaDB (se for a primeira execução ou se a pasta `backend/vector_db` não existir):
```bash
python -m backend.scripts.index_documents
```

4. Inicie o servidor do Backend **a partir do diretório raiz**:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
> O backend estará disponível em `http://localhost:8000` (Documentação Swagger em `http://localhost:8000/docs`).

---

### Passo 4: Configurar e Iniciar o Frontend (React + Vite)

Abra uma **segunda janela de terminal**, navegue até a pasta `frontend` e execute:

```bash
# Entrar na pasta do frontend:
cd frontend

# Instalar as dependências do Node:
npm install

# Iniciar o servidor de desenvolvimento:
npm run dev
```

> O frontend estará rodando em **`http://localhost:3000`** (ou porta informada pelo Vite).

---

## ❓ Solução de Problemas Comuns (Troubleshooting)

### 1. `ModuleNotFoundError: No module named 'chromadb'` ou `httpx`
- **Causa**: O ambiente virtual Python não foi ativado ou as dependências não foram instaladas via `requirements.txt`.
- **Solução**: Certifique-se de ter rodado `pip install -r requirements.txt` no seu `.venv`.

### 2. Mensagem: *"Não foi possível conectar ao Ollama. Verifique se ele está em execução."*
- **Causa**: O serviço do Ollama não está rodando ou os modelos não foram baixados.
- **Solução**: Abra o Ollama e execute `ollama pull nomic-embed-text` e `ollama pull gemma3:4b`.

### 3. `ModuleNotFoundError: No module named 'backend'` ao rodar o Uvicorn
- **Causa**: O comando do Uvicorn foi executado de dentro da pasta `backend/` em vez da raiz do projeto.
- **Solução**: Volte para a raiz (`cd ..`) e execute `python -m uvicorn backend.main:app --reload --port 8000`.

### 4. Mensagem no Chat: *"Não consegui me conectar ao serviço da Zophia agora"*
- **Causa**: O frontend (porta 3000) não conseguiu se comunicar com o backend (porta 8000).
- **Solução**: Verifique se o servidor do Uvicorn está rodando na porta 8000.

---

## 📋 Estrutura da Resposta RAG (7 Seções)

As respostas geradas e disponibilizadas sob demanda seguem os parâmetros da base documental:

1. **Resumo Acolhedor** (`RAG: LLM`)
2. **Sinais Observados** (`RAG: DSM-5-TR`)
3. **Informações Educativas** (`RAG: DSM-5-TR / NICE`)
4. **Cuidados Sugeridos** (`RAG: WHO mhGAP / NICE`)
5. **Quando Procurar Ajuda Profissional** (`RAG: mhGAP / RAPS`)
6. **Fontes Utilizadas** (Base Documental)
7. **Aviso de Segurança** (Orientação educacional e CVV 188)

---

## 👥 Integrantes

- Pablo Odilon Agra de Queiroz
- Deyvid Jeronimo De Araujo Macedo 
- Kaio Emanuel Rosemiro de Carvalho
- Luiz Jose Mendonca Duarte
