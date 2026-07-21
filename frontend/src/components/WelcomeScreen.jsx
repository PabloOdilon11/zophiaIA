import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Smile, Wind, Book, Sparkles, Moon, HeartPulse } from 'lucide-react';
import SuggestionCard from './SuggestionCard';

export default function WelcomeScreen({ onSelectSuggestion }) {
  const [selectedMood, setSelectedMood] = useState(null);

  const moods = [
    { label: 'Feliz', emoji: '😊', color: 'hover:bg-amber-50 hover:border-amber-300', prompt: 'Estou me sentindo feliz e bem hoje! Gostaria de conversar um pouco.' },
    { label: 'Neutro', emoji: '😐', color: 'hover:bg-slate-50 hover:border-slate-300', prompt: 'Estou me sentindo num dia neutro e tranquilo. Como podemos conversar?' },
    { label: 'Triste', emoji: '😔', color: 'hover:bg-blue-50 hover:border-blue-300', prompt: 'Estou me sentindo um pouco triste e desanimado hoje...' },
    { label: 'Ansioso', emoji: '😰', color: 'hover:bg-purple-50 hover:border-purple-300', prompt: 'Estou me sentindo ansioso e com a mente um pouco agitada.' },
    { label: 'Cansado', emoji: '😫', color: 'hover:bg-orange-50 hover:border-orange-300', prompt: 'Estou me sentindo bastante cansado e exausto mentalmente.' },
  ];

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'Bom dia';
    if (hour >= 12 && hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const suggestions = [
    {
      icon: Wind,
      title: "Entender minha ansiedade",
      prompt: "Quero entender melhor como lidar com os sintomas de ansiedade no meu dia a dia."
    },
    {
      icon: Moon,
      title: "Cuidar do meu sono",
      prompt: "Estou tendo dificuldades para dormir bem e desacelerar a mente à noite."
    },
    {
      icon: Book,
      title: "Organizar pensamentos",
      prompt: "Preciso de ajuda para organizar meus pensamentos e sentimentos acumulados."
    },
    {
      icon: Smile,
      title: "Conversar sobre o dia",
      prompt: "Quero apenas conversar um pouco sobre como foi meu dia."
    }
  ];

  const handleMoodSelect = (mood) => {
    setSelectedMood(mood.label);
    onSelectSuggestion(mood.prompt);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-xl mx-auto py-2 px-4 text-center flex flex-col items-center justify-center min-h-[55vh]"
    >
      {/* Circular Avatar */}
      <div className="relative mb-2">
        <div className="w-20 h-20 rounded-full bg-zophia-pink/15 p-1 shadow-md shadow-zophia-pink/10 border border-zophia-pink/30">
          <div className="w-full h-full bg-white rounded-full flex items-center justify-center p-2.5 shadow-inner">
            <img 
              src="/zophia_mini_logo.png" 
              onError={(e) => { e.target.src = '/assets/zophia_mini_logo.png'; }}
              alt="Zophia Logo" 
              className="w-14 h-14 object-contain" 
            />
          </div>
        </div>
        <div className="absolute top-0 right-0 bg-white p-1 rounded-full shadow-xs border border-zophia-border">
          <Sparkles className="w-3.5 h-3.5 text-zophia-pink fill-zophia-pink" />
        </div>
      </div>

      <h2 className="font-heading font-extrabold text-2xl md:text-3xl text-zophia-text tracking-tight mt-0.5">
        {getGreeting()}! Eu sou a <span className="text-zophia-purple">Zophia</span> 💜
      </h2>

      <p className="text-slate-600 mt-1 max-w-md text-sm leading-snug">
        Estou aqui para ouvir, conversar e apoiar você de forma acolhedora.
      </p>

      {/* Emotional Check-in Section */}
      <div className="w-full mt-4 bg-white/70 p-3.5 rounded-2xl border border-zophia-border shadow-2xs">
        <p className="text-xs font-bold text-zophia-purple mb-2 flex items-center justify-center gap-1.5">
          <HeartPulse size={14} className="text-zophia-pink" />
          Como você está se sentindo hoje?
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {moods.map((m) => (
            <button
              key={m.label}
              onClick={() => handleMoodSelect(m)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-semibold transition-all ${m.color} ${
                selectedMood === m.label ? 'bg-zophia-purple text-white border-zophia-purple shadow-2xs' : 'bg-white text-slate-700 border-zophia-border'
              }`}
            >
              <span>{m.emoji}</span>
              <span>{m.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Suggestions Grid (2x2 layout) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 w-full mt-4">
        {suggestions.map((item, idx) => (
          <SuggestionCard 
            key={idx}
            icon={item.icon}
            title={item.title}
            onClick={() => onSelectSuggestion(item.prompt)}
          />
        ))}
      </div>
    </motion.div>
  );
}
