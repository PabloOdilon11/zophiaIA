# Zophia - Assistente Inteligente de Apoio à Saúde Mental 💜

## Sobre o Projeto

O **Zophia** é uma aplicação web moderna voltada para o acolhimento, escuta atenta e apoio educacional em saúde mental. 

O sistema combina um **Frontend moderno em React** (estilo ChatGPT/Claude) com um **Backend em Python/FastAPI** embasado na arquitetura **Retrieval-Augmented Generation (RAG)** e documentos científicos de referência.

Este projeto está sendo desenvolvido para a disciplina de Inteligência Artificial da Universidade Estadual da Paraíba (**UEPB**).

---

## 🚀 Status Atual do Projeto

- **Frontend**: Migrado e reconstruído em **React + Vite + TailwindCSS + Lucide React + Framer Motion**.
- **Backend**: API REST em **FastAPI + Pydantic** com endpoints de análise estruturada e métricas de dataset.
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
- **Pandas**
- **FAISS** & **Sentence Transformers** (Busca semântica RAG)

---

## 📁 Estrutura de Diretórios

```
zophiaIA/
├── backend/
│   ├── main.py                # Ponto de entrada FastAPI (CORS, Rotas)
│   ├── models/                # Schemas Pydantic de validação
│   └── services/              # Serviços de classificação e análise de relatos
├── frontend/
│   ├── index.html             # HTML principal com favicon
│   ├── package.json           # Dependências React e Scripts Vite
│   ├── tailwind.config.js     # Configuração de temas e cores sólidas Zophia
│   ├── public/                # Assets e logos estáticas (zophia_logo, zophia_mini_logo)
│   └── src/
│       ├── App.jsx            # Aplicação React principal
│       ├── components/        # Sidebar, Header, ChatMessage, ChatInput, ToolModal, etc.
│       └── styles/            # CSS global e diretivas Tailwind
├── dataset/                   # Relatos utilizados nos testes e análises
├── documents/                 # Base documental RAG (WHO mhGAP, NICE, DSM-5-TR, RAPS, CVV)
└── requirements.txt           # Dependências Python do backend
```

---

## 🛠️ Como Instalar e Rodar o Projeto (Status Atual)

### 1. Clonar a branch `new-frontend`
```bash
git clone https://github.com/PabloOdilon11/zophiaIA.git
cd zophiaIA
git checkout new-frontend
```

### 2. Configurar e Iniciar o Backend (FastAPI)

1. Crie e ative um ambiente virtual Python (opcional, mas recomendado):
```bash
python -m venv .venv
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Linux/Mac:
source .venv/bin/activate
```

2. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

3. Inicie o servidor do Backend na porta `8000`:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
> O backend estará rodando em `http://localhost:8000` (Documentação Swagger em `http://localhost:8000/docs`).

---

### 3. Configurar e Iniciar o Frontend (React + Vite)

Em uma nova janela de terminal, navegue até a pasta `frontend`:

1. Instale as dependências do Node:
```bash
cd frontend
npm install
```

2. Inicie o servidor de desenvolvimento do Frontend:
```bash
npm run dev
```

3. Acesse a aplicação no seu navegador:
> **`http://localhost:3000`** (ou a porta indicada pelo Vite).

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
