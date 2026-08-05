from dataclasses import dataclass, field
from threading import Lock
from typing import Literal
from uuid import uuid4


Role = Literal["user", "assistant"]


@dataclass
class ConversationMessage:
    role: Role
    content: str


@dataclass
class Conversation:
    conversation_id: str
    messages: list[ConversationMessage] = field(default_factory=list)
    crisis_active: bool = False


class ConversationManager:
    """
    Armazena conversas temporariamente na memória do servidor.

    Nesta primeira versão, o histórico é apagado quando
    o backend é reiniciado.
    """

    def __init__(self, max_messages: int = 12) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._max_messages = max_messages
        self._lock = Lock()

    def create_conversation(self) -> str:
        conversation_id = str(uuid4())

        with self._lock:
            self._conversations[conversation_id] = Conversation(
                conversation_id=conversation_id
            )

        return conversation_id

    def get_or_create_conversation(
        self,
        conversation_id: str | None,
    ) -> Conversation:
        with self._lock:
            if (
                conversation_id
                and conversation_id in self._conversations
            ):
                return self._conversations[conversation_id]

            new_id = conversation_id or str(uuid4())

            conversation = Conversation(
                conversation_id=new_id
            )

            self._conversations[new_id] = conversation

            return conversation

    def add_message(
        self,
        conversation_id: str,
        role: Role,
        content: str,
    ) -> None:
        content = content.strip()

        if not content:
            return

        with self._lock:
            conversation = self._conversations.get(
                conversation_id
            )

            if conversation is None:
                conversation = Conversation(
                    conversation_id=conversation_id
                )

                self._conversations[conversation_id] = conversation

            conversation.messages.append(
                ConversationMessage(
                    role=role,
                    content=content,
                )
            )

            if len(conversation.messages) > self._max_messages:
                conversation.messages = conversation.messages[
                    -self._max_messages:
                ]

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[ConversationMessage]:
        with self._lock:
            conversation = self._conversations.get(
                conversation_id
            )

            if conversation is None:
                return []

            return list(conversation.messages)

    def build_history(
        self,
        conversation_id: str,
        exclude_last_user_message: bool = False,
    ) -> str:
        messages = self.get_messages(conversation_id)

        if (
            exclude_last_user_message
            and messages
            and messages[-1].role == "user"
        ):
            messages = messages[:-1]

        if not messages:
            return "Nenhuma mensagem anterior."

        formatted_messages: list[str] = []

        for message in messages:
            speaker = (
                "Usuário"
                if message.role == "user"
                else "Zophia"
            )

            formatted_messages.append(
                f"{speaker}: {message.content}"
            )

        return "\n\n".join(formatted_messages)

    def build_search_query(
        self,
        conversation_id: str,
        current_question: str,
        previous_user_messages: int = 2,
    ) -> str:
        """
        Acrescenta perguntas anteriores à consulta enviada ao RAG.

        Isso ajuda mensagens como:
        - "e quanto tempo?"
        - "explique melhor"
        - "e o tratamento?"
        """

        messages = self.get_messages(conversation_id)

        user_messages = [
            message.content
            for message in messages
            if message.role == "user"
        ]

        if (
            user_messages
            and user_messages[-1].strip()
            == current_question.strip()
        ):
            user_messages = user_messages[:-1]

        previous_messages = user_messages[
            -previous_user_messages:
        ]

        if not previous_messages:
            return current_question

        return "\n".join(
            [
                "Contexto das perguntas anteriores:",
                *previous_messages,
                "",
                f"Pergunta atual: {current_question}",
            ]
        )

    def set_crisis_active(
        self,
        conversation_id: str,
        active: bool,
    ) -> None:
        with self._lock:
            conversation = self._conversations.get(
                conversation_id
            )

            if conversation is None:
                conversation = Conversation(
                    conversation_id=conversation_id
                )

                self._conversations[conversation_id] = conversation

            conversation.crisis_active = active

    def is_crisis_active(
        self,
        conversation_id: str,
    ) -> bool:
        with self._lock:
            conversation = self._conversations.get(
                conversation_id
            )

            return bool(
                conversation
                and conversation.crisis_active
            )

    def clear_conversation(
        self,
        conversation_id: str,
    ) -> None:
        with self._lock:
            self._conversations.pop(
                conversation_id,
                None,
            )


conversation_manager = ConversationManager(
    max_messages=100
)