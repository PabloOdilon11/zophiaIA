# Zophia - Redesign da Interface Web

## Objetivo

Migrar a interface atual da Zophia (Streamlit) para uma aplicação web moderna, mantendo a identidade visual da marca e criando uma experiência semelhante aos principais chats de IA atuais (ChatGPT, Claude, Perplexity).

A prioridade é criar uma interface acolhedora, profissional e intuitiva para um assistente inteligente de apoio à saúde mental.

O projeto é acadêmico e possui aproximadamente 1 mês de desenvolvimento, portanto a solução deve priorizar velocidade de implementação, simplicidade e qualidade visual.

---

# Stack definida

## Frontend

Utilizar:

- React + Vite
- TailwindCSS
- Shadcn/UI
- Lucide React Icons
- Framer Motion para animações

## Backend

Manter Python:

- FastAPI
- Endpoints REST

A lógica atual de análise de mensagens pode ser reaproveitada.

---

# Objetivo visual

A interface deve transmitir:

- acolhimento;
- segurança;
- tecnologia;
- calma;
- profissionalismo.

Evitar aparência de dashboard administrativo.

A aplicação deve parecer um produto real.

---

# Layout principal

A tela deve possuir três áreas:

```

-------------------------------------------------
| Sidebar |              Chat             | Tools |
|         |                               |       |
|         |                               |       |
-------------------------------------------------

```

---

# Sidebar

Responsável por navegação.

Elementos:

## Logo

Exibir logo Zophia.

## Menu

Itens:

- Nova conversa
- Conversas recentes

Exemplo:

```
Nova conversa

Conversas recentes

• Ansiedade e rotina
• Como lidar com tristeza
• Autoconhecimento
• Sono e bem-estar

```

## Explorar

Itens:

- Base documental
- Dataset e métricas
- Recursos

## Rodapé

Card:

"Uso responsável"

Texto:

"A Zophia é uma ferramenta educacional e não substitui atendimento psicológico, psiquiátrico ou médico."

---

# Área principal do Chat

## Estado inicial

Quando não existe conversa:

Mostrar:

```

🧠

Olá! Eu sou a Zophia 💜

Estou aqui para ouvir, conversar e apoiar você.

Como você está se sentindo hoje?

```

---

Adicionar sugestões rápidas:

Cards pequenos:

- Quero entender melhor minha ansiedade
- Como cuidar do meu sono?
- Preciso organizar meus pensamentos
- Quero conversar sobre meu dia

---

# Conversas

As mensagens devem utilizar estilo ChatGPT.

## Mensagem da Zophia

Formato:

```

🧠 Zophia

┌─────────────────────┐
Olá!
Como posso ajudar você?
└─────────────────────┘

```

Características:

- fundo branco;
- bordas arredondadas;
- sombra suave;
- avatar da Zophia.

---

## Mensagem do usuário

Formato:

```

                 Usuário

       ┌─────────────────┐
       Estou ansioso hoje
       └─────────────────┘

```

Características:

- alinhada à direita;
- fundo roxo/rosa;
- texto branco.

---

# Input de mensagem

Criar um campo semelhante aos chats modernos.

Características:

- fixo na parte inferior;
- bordas arredondadas;
- sombra;
- botão enviar.

Exemplo:

```

╭────────────────────────╮
 Escreva sua mensagem...      ➤
╰────────────────────────╯

```

---

# Painel lateral direito

Adicionar ferramentas rápidas.

Cards:

## Exercício de respiração

Ícone:
🌱

Descrição:

"Pratique uma técnica rápida para reduzir tensão."

---

## Diário emocional

Ícone:
📖

Descrição:

"Registre pensamentos e sentimentos."

---

## Reflexão guiada

Ícone:
💜

Descrição:

"Perguntas para autoconhecimento."

---

## Relaxamento

Ícone:
🎧

Descrição:

"Exercícios rápidos."

---

# Card de mensagem do dia

Adicionar:

```

Mensagem do dia

"Você não precisa resolver tudo hoje."

❤️

```

---

# Identidade visual

Utilizar as cores atuais da Zophia:

Principal:

Purple:
#8D3F9E

Pink:
#ED4F9D

Background:

#FCF8F7

Texto:

#292331

---

# Tipografia

Usar:

- Manrope para títulos
- DM Sans para textos

---

# Componentização

Criar componentes separados:

```

src/

components/

    Sidebar.jsx

    ChatWindow.jsx

    ChatMessage.jsx

    ChatInput.jsx

    WelcomeScreen.jsx

    SuggestionCard.jsx

    ToolCard.jsx

    Header.jsx

```

---

# Estrutura esperada

```

frontend/

src/

 components/

 pages/

 styles/

 assets/

 App.jsx

 main.jsx


backend/

 main.py

 services/

 models/

```

---

# Animações

Adicionar:

- entrada suave das mensagens;
- efeito de digitação da IA;
- hover nos cards;
- transições suaves.

Usar Framer Motion.

---

# Responsividade

A aplicação deve funcionar em:

- desktop;
- notebook;
- tablet.

No mobile:

- esconder painel direito;
- transformar sidebar em menu.

---

# Regras importantes

Não criar uma interface parecida com dashboard.

Priorizar:

- conversa;
- conforto visual;
- simplicidade.

A experiência deve parecer conversar com uma assistente inteligente humana.

---

# Prioridade de implementação

## Fase 1

Criar layout completo.

## Fase 2

Criar componentes do chat.

## Fase 3

Conectar FastAPI.

## Fase 4

Adicionar detalhes visuais.

## Fase 5

Polimento final.

---

# Resultado esperado

Uma interface web moderna de chatbot de saúde mental com aparência profissional, mantendo a identidade da Zophia e adequada para apresentação universitária.