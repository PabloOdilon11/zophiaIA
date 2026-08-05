import React, { useState } from 'react';
import { Leaf, BookOpen, Heart, Headphones, Sun, ChevronRight, ChevronLeft } from 'lucide-react';
import ToolCard from './ToolCard';

export default function RightPanel({ onSelectTool }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const tools = [
    {
      id: 'breath',
      icon: Leaf,
      title: "Exercício de respiração",
      description: "Pratique uma técnica rápida para reduzir tensão.",
      tag: "Guiado"
    },
    {
      id: 'journal',
      icon: BookOpen,
      title: "Diário emocional",
      description: "Registre pensamentos e sentimentos.",
      tag: "Autoconhecimento"
    },
    {
      id: 'reflection',
      icon: Heart,
      title: "Reflexão guiada",
      description: "Perguntas para autoconhecimento.",
      tag: "Reflexão"
    },
    {
      id: 'relax',
      icon: Headphones,
      title: "Relaxamento",
      description: "Exercícios rápidos.",
      tag: "Bem-estar"
    }
  ];

  if (isCollapsed) {
    return (
      <aside className="w-10 border-l border-zophia-border bg-white/50 flex flex-col items-center hidden lg:flex overflow-y-auto">
        <button
          onClick={() => setIsCollapsed(false)}
          title="Expandir Cuidado Diário"
          aria-label="Expandir Cuidado Diário"
          className="mt-4 p-2 rounded-xl text-zophia-purple hover:bg-zophia-pink/10 transition-colors"
        >
          <ChevronLeft size={18} />
        </button>
      </aside>
    );
  }

  return (
    <aside className="w-80 border-l border-zophia-border bg-white/50 p-5 flex flex-col justify-between hidden lg:flex overflow-y-auto">
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-heading font-bold text-base text-zophia-purple">Cuidado Diário</h3>
            <p className="text-xs text-gray-500 mt-0.5">Recursos da Zophia para o seu bem-estar</p>
          </div>
          <button
            onClick={() => setIsCollapsed(true)}
            title="Recolher Cuidado Diário"
            aria-label="Recolher Cuidado Diário"
            className="p-2 rounded-xl text-zophia-purple hover:bg-zophia-pink/10 transition-colors -mt-1 -mr-1"
          >
            <ChevronRight size={18} />
          </button>
        </div>

        <div className="space-y-3">
          {tools.map(t => (
            <ToolCard 
              key={t.id}
              icon={t.icon}
              title={t.title}
              description={t.description}
              tag={t.tag}
              onClick={() => onSelectTool(t)}
            />
          ))}
        </div>

        {/* Daily Message Card */}
        <div className="bg-zophia-sidebar border border-zophia-pink/20 rounded-2xl p-4 mt-6 text-center space-y-2 relative overflow-hidden">
          <div className="absolute -top-3 -right-3 text-zophia-pink/20">
            <Sun size={60} />
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-zophia-pink bg-white/80 px-2.5 py-0.5 rounded-full inline-block">
            Mensagem do dia
          </span>
          <p className="font-heading font-bold text-sm text-zophia-purple italic">
            "Você não precisa resolver tudo hoje."
          </p>
          <div className="flex justify-center pt-1 text-zophia-pink">
            <Heart size={14} className="fill-zophia-pink" />
          </div>
        </div>
      </div>
    </aside>
  );
}