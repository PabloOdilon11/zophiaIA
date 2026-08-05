import React from 'react';
import { Menu, Heart } from 'lucide-react';

export default function Header({ onOpenSidebar }) {
  return (
    <header className="h-16 border-b border-zophia-border bg-white/70 backdrop-blur-md px-4 md:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button 
          onClick={onOpenSidebar}
          className="md:hidden p-2 hover:bg-zophia-bg rounded-xl text-zophia-text"
        >
          <Menu size={20} />
        </button>

        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <h2 className="font-heading font-bold text-gray-800 text-sm md:text-base">Zophia Lite</h2>
          <span className="text-xs bg-zophia-pink/10 text-zophia-pink px-2.5 py-0.5 rounded-full font-semibold border border-zophia-pink/20">
            Assistente de Bem-estar
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-gray-500 font-medium">
        <Heart size={14} className="text-zophia-pink fill-zophia-pink" />
        <span className="hidden sm:inline">Ambiente Seguro & Acolhedor</span>
      </div>
    </header>
  );
}
