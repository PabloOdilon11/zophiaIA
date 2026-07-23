import React, { useEffect, useRef, useState } from 'react';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import RightPanel from './components/RightPanel';
import WelcomeScreen from './components/WelcomeScreen';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DocsView from './components/DocsView';
import MetricsView from './components/MetricsView';
import ToolModal from './components/ToolModal';

const API_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedTool, setSelectedTool] = useState(null);

  const [chats, setChats] = useState([
    {
      id: '1',
      title: 'Ansiedade e rotina',
      messages: [],
    },
    {
      id: '2',
      title: 'Como lidar com tristeza',
      messages: [],
    },
    {
      id: '3',
      title: 'Sono e bem-estar',
      messages: [],
    },
  ]);

  const [activeChatId, setActiveChatId] = useState('1');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const activeChat =
    chats.find((chat) => chat.id === activeChatId) || chats[0];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeChat?.messages, isLoading]);

  const handleNewChat = () => {
    const newId = Date.now().toString();

    const newChat = {
      id: newId,
      title: 'Nova conversa',
      messages: [],
    };

    setChats((previousChats) => [
      newChat,
      ...previousChats,
    ]);

    setActiveChatId(newId);
    setActiveTab('chat');
  };

  const addMessageToChat = (chatId, message) => {
    setChats((previousChats) =>
      previousChats.map((chat) => {
        if (chat.id !== chatId) {
          return chat;
        }

        return {
          ...chat,
          messages: [
            ...chat.messages,
            message,
          ],
        };
      }),
    );
  };

  const handleSendMessage = async (text) => {
    const cleanText = text.trim();

    if (!cleanText || isLoading) {
      return;
    }

    const currentChatId = activeChatId;

    const userMessage = {
      id: `${Date.now()}-user`,
      sender: 'user',
      text: cleanText,
    };

    setChats((previousChats) =>
      previousChats.map((chat) => {
        if (chat.id !== currentChatId) {
          return chat;
        }

        const isFirstMessage = chat.messages.length === 0;

        const newTitle = isFirstMessage
          ? `${cleanText.slice(0, 24)}${
              cleanText.length > 24 ? '...' : ''
            }`
          : chat.title;

        return {
          ...chat,
          title: newTitle,
          messages: [
            ...chat.messages,
            userMessage,
          ],
        };
      }),
    );

    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: cleanText,
        }),
      });

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          'O backend retornou uma resposta inválida.',
        );
      }

      if (!response.ok) {
        const errorMessage =
          typeof data.detail === 'string'
            ? data.detail
            : 'Não foi possível obter uma resposta da Zophia.';

        throw new Error(errorMessage);
      }

      if (!data.response) {
        throw new Error(
          'A resposta da Zophia veio vazia.',
        );
      }

      const zophiaMessage = {
        id: `${Date.now()}-zophia`,
        sender: 'zophia',
        text: data.response,
        model: data.model,
      };

      addMessageToChat(
        currentChatId,
        zophiaMessage,
      );
    } catch (error) {
      console.error(
        'Erro ao conectar com a Zophia:',
        error,
      );

      const errorMessage = {
        id: `${Date.now()}-error`,
        sender: 'zophia',
        text:
          'Não consegui me conectar ao serviço da Zophia agora. Verifique se o backend e o Ollama estão ligados e tente novamente.',
        isError: true,
      };

      addMessageToChat(
        currentChatId,
        errorMessage,
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectTool = (tool) => {
    setSelectedTool(tool);
  };

  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
    setActiveTab('chat');
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zophia-bg font-body text-zophia-text">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
      />

      <div className="flex h-full min-w-0 flex-1 flex-col">
        <Header
          onOpenSidebar={() =>
            setSidebarOpen(true)
          }
        />

        <main className="relative flex-1 overflow-y-auto">
          {activeTab === 'chat' && (
            <>
              {activeChat?.messages.length === 0 ? (
                <WelcomeScreen
                  onSelectSuggestion={
                    handleSendMessage
                  }
                />
              ) : (
                <div className="mx-auto max-w-3xl space-y-4 px-4 py-6">
                  {activeChat?.messages.map(
                    (message) => (
                      <ChatMessage
                        key={message.id}
                        message={message}
                      />
                    ),
                  )}

                  {isLoading && (
                    <div className="my-2 flex w-fit items-center gap-2.5 rounded-2xl border border-zophia-border bg-white/80 p-3.5 text-xs font-semibold text-zophia-purple shadow-xs animate-pulse">
                      <div className="flex items-center gap-1">
                        <span
                          className="h-1.5 w-1.5 animate-bounce rounded-full bg-zophia-pink"
                          style={{
                            animationDelay: '0ms',
                          }}
                        />

                        <span
                          className="h-1.5 w-1.5 animate-bounce rounded-full bg-zophia-purple"
                          style={{
                            animationDelay: '150ms',
                          }}
                        />

                        <span
                          className="h-1.5 w-1.5 animate-bounce rounded-full bg-zophia-pink"
                          style={{
                            animationDelay: '300ms',
                          }}
                        />
                      </div>

                      <span>
                        Zophia está pensando...
                      </span>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              )}
            </>
          )}

          {activeTab === 'docs' && (
            <DocsView />
          )}

          {activeTab === 'metrics' && (
            <MetricsView />
          )}
        </main>

        {activeTab === 'chat' && (
          <ChatInput
            onSendMessage={
              handleSendMessage
            }
            isLoading={isLoading}
          />
        )}
      </div>

      {activeTab === 'chat' && (
        <RightPanel
          onSelectTool={handleSelectTool}
        />
      )}

      <ToolModal
        tool={selectedTool}
        onClose={() =>
          setSelectedTool(null)
        }
      />
    </div>
  );
}