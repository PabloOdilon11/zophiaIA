import React from 'react';
import { Plus, MessageSquare, BookOpen, BarChart2, ShieldAlert, Sparkles, X } from 'lucide-react';

export default function Sidebar({ isOpen, onClose, activeTab, setActiveTab, chats, activeChatId, onNewChat, onSelectChat }) {
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/40 z-40 md:hidden backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />
      )}

      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-72 bg-zophia-sidebar border-r border-zophia-border
        flex flex-col justify-between
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="p-4 overflow-y-auto space-y-6">
          {/* Header & Logo */}
          <div className="flex items-center justify-between px-2 pt-1 pb-2">
            <div className="flex items-center w-full">
              <img 
                src="/zophia_logo.png" 
                onError={(e) => { e.target.src = '/assets/zophia_logo.png'; }}
                alt="Zophia Logo" 
                className="w-full max-w-[240px] h-auto object-contain py-1 drop-shadow-xs" 
              />
            </div>
            <button onClick={onClose} className="md:hidden p-1 text-gray-500 hover:text-gray-700">
              <X size={20} />
            </button>
          </div>

          {/* New Chat Button */}
          <button 
            onClick={() => { onNewChat(); onClose(); }}
            className="w-full flex items-center justify-center gap-2.5 bg-white text-zophia-purple border border-zophia-pink/30 hover:border-zophia-pink/60 font-semibold py-2.5 px-4 rounded-2xl shadow-2xs hover:shadow-sm hover:bg-zophia-pink/5 transition-all duration-200"
          >
            <Plus size={18} className="text-zophia-pink" />
            <span>Nova conversa</span>
          </button>

          {/* Navigation Menu */}
          <div className="space-y-1">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Conversas recentes</p>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {chats.map(chat => (
                <button
                  key={chat.id}
                  onClick={() => { onSelectChat(chat.id); onClose(); }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors text-left truncate ${
                    activeChatId === chat.id 
                      ? 'bg-white text-zophia-purple shadow-sm border border-zophia-border/60' 
                      : 'text-zophia-text/80 hover:bg-white/60 hover:text-zophia-purple'
                  }`}
                >
                  <MessageSquare size={16} className="shrink-0 text-zophia-pink" />
                  <span className="truncate">{chat.title}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Explore Menu */}
          <div className="space-y-1 pt-2 border-t border-zophia-border/60">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Explorar</p>
            
            <button
              onClick={() => { setActiveTab('chat'); onClose(); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                activeTab === 'chat' 
                  ? 'bg-white text-zophia-purple shadow-sm border border-zophia-border/60' 
                  : 'text-zophia-text/80 hover:bg-white/60 hover:text-zophia-purple'
              }`}
            >
              <Sparkles size={16} className="text-zophia-purple" />
              <span>Assistente Conversacional</span>
            </button>

            <button
              onClick={() => { setActiveTab('docs'); onClose(); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                activeTab === 'docs' 
                  ? 'bg-white text-zophia-purple shadow-sm border border-zophia-border/60' 
                  : 'text-zophia-text/80 hover:bg-white/60 hover:text-zophia-purple'
              }`}
            >
              <BookOpen size={16} className="text-zophia-purple" />
              <span>Base documental</span>
            </button>

            <button
              onClick={() => { setActiveTab('metrics'); onClose(); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                activeTab === 'metrics' 
                  ? 'bg-white text-zophia-purple shadow-sm border border-zophia-border/60' 
                  : 'text-zophia-text/80 hover:bg-white/60 hover:text-zophia-purple'
              }`}
            >
              <BarChart2 size={16} className="text-zophia-purple" />
              <span>Dataset e métricas</span>
            </button>
          </div>
        </div>

        {/* Footer Card */}
        <div className="p-4 border-t border-zophia-border/60">
          <div className="bg-white/80 p-3.5 rounded-2xl border border-zophia-border shadow-2xs space-y-1">
            <div className="flex items-center gap-2 text-zophia-purple font-heading font-bold text-xs">
              <ShieldAlert size={14} className="text-zophia-pink" />
              <span>Uso responsável</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-relaxed">
              A Zophia é uma ferramenta educacional e não substitui atendimento psicológico ou médico.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
