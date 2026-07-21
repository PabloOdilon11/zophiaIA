# Como rodar a Zophia (React + FastAPI)

Este guia explica como iniciar a aplicação Zophia com o novo frontend em **React + Vite** e backend em **FastAPI**.

## 1. Pré-requisitos

- Python 3.10 ou superior
- Node.js 18 ou superior

## 2. Iniciar o Backend (FastAPI)

No terminal, na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

O servidor da API estará disponível em: `http://localhost:8000` (documentação Swagger em `http://localhost:8000/docs`).

## 3. Iniciar o Frontend (React + Vite)

Em outro terminal, acesse a pasta `frontend`:

```powershell
cd frontend
npm run dev
```

Acesse a interface gráfica no seu navegador em: `http://localhost:3000`

---

## Estrutura do Projeto

- `backend/`: Código da API em Python (FastAPI, schemas Pydantic, serviços de análise).
- `frontend/`: Aplicação web moderna em React, Vite, TailwindCSS, Lucide React e Framer Motion.
