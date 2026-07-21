import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import RightPanel from './components/RightPanel';
import WelcomeScreen from './components/WelcomeScreen';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DocsView from './components/DocsView';
import MetricsView from './components/MetricsView';

import ToolModal from './components/ToolModal';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedTool, setSelectedTool] = useState(null);
  const [chats, setChats] = useState([
    { id: '1', title: 'Ansiedade e rotina', messages: [] },
    { id: '2', title: 'Como lidar com tristeza', messages: [] },
    { id: '3', title: 'Sono e bem-estar', messages: [] }
  ]);
  const [activeChatId, setActiveChatId] = useState('1');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const activeChat = chats.find(c => c.id === activeChatId) || chats[0];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeChat?.messages, isLoading]);

  const handleNewChat = () => {
    const newId = Date.now().toString();
    const newChat = { id: newId, title: 'Nova conversa', messages: [] };
    setChats(prev => [newChat, ...prev]);
    setActiveChatId(newId);
    setActiveTab('chat');
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // Append user message
    const userMsg = { id: Date.now().toString(), sender: 'user', text };
    
    setChats(prev => prev.map(chat => {
      if (chat.id === activeChatId) {
        const title = chat.messages.length === 0 ? text.slice(0, 24) + '...' : chat.title;
        return {
          ...chat,
          title,
          messages: [...chat.messages, userMsg]
        };
      }
      return chat;
    }));

    setIsLoading(true);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await response.json();

      let botText = "Obrigado por compartilhar o que está sentindo com a Zophia.";
      if (data.report_type === 'positive') {
        botText = "Que bom saber que você está vivendo um momento positivo! Reconhecer suas conquistas e sentimentos bons é fundamental para o bem-estar.";
      } else if (data.report_type === 'distress' || data.report_type === 'risk') {
        botText = "Agradeço por compartilhar seus sentimentos. É muito importante dar atenção aos sinais de desconforto e buscar acolhimento.";
      }

      const botMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'zophia',
        text: botText,
        analysis: data
      };

      setChats(prev => prev.map(chat => {
        if (chat.id === activeChatId) {
          return { ...chat, messages: [...chat.messages, botMsg] };
        }
        return chat;
      }));
    } catch (err) {
      const fallbackMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'zophia',
        text: "Obrigado por compartilhar. A Zophia está aqui para oferecer apoio e escuta atenta aos seus sentimentos."
      };
      setChats(prev => prev.map(chat => {
        if (chat.id === activeChatId) {
          return { ...chat, messages: [...chat.messages, fallbackMsg] };
        }
        return chat;
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectTool = (tool) => {
    setSelectedTool(tool);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zophia-bg font-body text-zophia-text">
      {/* Sidebar Navigation */}
      <Sidebar 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={(id) => { setActiveChatId(id); setActiveTab('chat'); }}
      />

      {/* Central Content Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        <Header onOpenSidebar={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-y-auto relative">
          {activeTab === 'chat' && (
            <>
              {activeChat.messages.length === 0 ? (
                <WelcomeScreen onSelectSuggestion={handleSendMessage} />
              ) : (
                <div className="px-4 py-6 max-w-3xl mx-auto space-y-4">
                  {activeChat.messages.map(msg => (
                    <ChatMessage key={msg.id} message={msg} />
                  ))}
                  {isLoading && (
                    <div className="flex items-center gap-2.5 text-xs text-zophia-purple font-semibold p-3.5 bg-white/80 rounded-2xl w-fit border border-zophia-border shadow-xs animate-pulse my-2">
                      <div className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-zophia-pink animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-zophia-purple animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-1.5 h-1.5 rounded-full bg-zophia-pink animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                      <span>Zophia está pensando...</span>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </>
          )}

          {activeTab === 'docs' && <DocsView />}
          {activeTab === 'metrics' && <MetricsView />}
        </main>

        {activeTab === 'chat' && (
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        )}
      </div>

      {/* Right Tools Panel */}
      {activeTab === 'chat' && (
        <RightPanel onSelectTool={handleSelectTool} />
      )}

      {/* Interactive Tool Modal */}
      <ToolModal tool={selectedTool} onClose={() => setSelectedTool(null)} />
    </div>
  );
}
