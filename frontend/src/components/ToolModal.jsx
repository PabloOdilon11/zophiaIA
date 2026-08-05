import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, Pause, RotateCcw, CheckCircle2, Heart, BookOpen, Leaf, Headphones } from 'lucide-react';

export default function ToolModal({ tool, onClose }) {
  if (!tool) return null;

  // Breathing state (4-7-8 method)
  const [breathPhase, setBreathPhase] = useState('Inhale'); // Inhale, Hold, Exhale
  const [breathCount, setBreathCount] = useState(4);
  const [isBreathingActive, setIsBreathingActive] = useState(false);

  // Journal state
  const [journalText, setJournalText] = useState('');
  const [journalSaved, setJournalSaved] = useState(false);

  useEffect(() => {
    let timer;
    if (tool.id === 'breath' && isBreathingActive) {
      timer = setInterval(() => {
        setBreathCount(prev => {
          if (prev > 1) return prev - 1;
          
          // Switch phase
          if (breathPhase === 'Inhale') {
            setBreathPhase('Hold');
            return 7;
          } else if (breathPhase === 'Hold') {
            setBreathPhase('Exhale');
            return 8;
          } else {
            setBreathPhase('Inhale');
            return 4;
          }
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [tool, isBreathingActive, breathPhase]);

  const renderContent = () => {
    switch (tool.id) {
      case 'breath':
        return (
          <div className="text-center space-y-6 py-4">
            <div className="relative w-40 h-40 mx-auto flex items-center justify-center">
              <motion.div 
                animate={{ 
                  scale: isBreathingActive && breathPhase === 'Inhale' ? 1.25 : isBreathingActive && breathPhase === 'Exhale' ? 0.85 : 1 
                }}
                transition={{ duration: breathPhase === 'Hold' ? 0 : 4, ease: "easeInOut" }}
                className="absolute inset-0 rounded-full bg-gradient-to-tr from-zophia-purple/20 to-zophia-pink/20 border border-zophia-pink/40 shadow-lg"
              />
              <div className="relative z-10 space-y-1">
                <div className="text-3xl font-extrabold text-zophia-purple">{breathCount}</div>
                <div className="text-xs font-bold uppercase tracking-wider text-zophia-pink">
                  {breathPhase === 'Inhale' ? 'Inspire' : breathPhase === 'Hold' ? 'Segure' : 'Expire'}
                </div>
              </div>
            </div>

            <p className="text-xs text-gray-500 max-w-xs mx-auto">
              Técnica 4-7-8: Inspire em 4s, segure por 7s e expire suavemente pela boca durante 8s.
            </p>

            <button
              onClick={() => setIsBreathingActive(!isBreathingActive)}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-zophia-purple to-zophia-pink text-white font-semibold py-2.5 px-6 rounded-2xl shadow-sm hover:opacity-95 transition-all text-xs"
            >
              {isBreathingActive ? <Pause size={16} /> : <Play size={16} />}
              <span>{isBreathingActive ? 'Pausar' : 'Iniciar exercício'}</span>
            </button>
          </div>
        );

      case 'journal':
        return (
          <div className="space-y-4 py-2">
            <p className="text-xs text-gray-600">
              Escreva livremente sobre como se sente. Este espaço é seu e suas anotações ficam gravadas apenas no seu navegador.
            </p>
            <textarea
              value={journalText}
              onChange={(e) => { setJournalText(e.target.value); setJournalSaved(false); }}
              placeholder="Como foi o seu dia? O que está na sua mente agora?..."
              rows={5}
              className="w-full p-3 text-xs bg-zophia-bg border border-zophia-border rounded-2xl focus:outline-none focus:border-zophia-pink/50 resize-none font-body text-zophia-text"
            />
            <div className="flex justify-between items-center">
              {journalSaved ? (
                <span className="text-xs text-emerald-600 font-medium flex items-center gap-1">
                  <CheckCircle2 size={14} /> Salvo com sucesso
                </span>
              ) : <span />}
              <button
                onClick={() => setJournalSaved(true)}
                disabled={!journalText.trim()}
                className="bg-zophia-purple text-white text-xs font-semibold py-2 px-4 rounded-xl disabled:opacity-50 hover:bg-zophia-purple/90"
              >
                Salvar registro
              </button>
            </div>
          </div>
        );

      case 'reflection':
        return (
          <div className="space-y-4 py-2">
            <div className="p-4 bg-zophia-bg rounded-2xl border border-zophia-border space-y-2">
              <h4 className="font-heading font-bold text-xs text-zophia-purple">Pergunta para hoje</h4>
              <p className="text-xs text-gray-700 italic">"Qual foi um pequeno momento de tranquilidade que você viveu hoje, mesmo no meio da rotina?"</p>
            </div>
            <p className="text-xs text-gray-500">
              Tirar alguns minutos para responder mentalmente a esta pergunta ajuda a direcionar a atenção para aspectos positivos e acolhedores.
            </p>
          </div>
        );

      case 'relax':
        return (
          <div className="space-y-4 py-2 text-center">
            <div className="p-5 bg-gradient-to-tr from-zophia-purple/10 to-zophia-pink/10 rounded-2xl border border-zophia-pink/20 space-y-3">
              <Headphones className="w-8 h-8 mx-auto text-zophia-purple animate-pulse" />
              <h4 className="font-heading font-bold text-xs text-zophia-purple">Relaxamento Muscular Progressivo</h4>
              <p className="text-xs text-gray-600 leading-relaxed">
                Feche os olhos, contraia suavemente os ombros por 5 segundos e solte de uma só vez. Repita 3 vezes e sinta a tensão ir embora.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-3xl border border-zophia-border shadow-xl max-w-md w-full p-5 space-y-4 relative"
        >
          <div className="flex items-center justify-between border-b border-zophia-border/60 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-zophia-bg text-zophia-purple">
                <tool.icon size={18} />
              </div>
              <div>
                <h3 className="font-heading font-bold text-sm text-zophia-purple">{tool.title}</h3>
                <span className="text-[10px] font-semibold text-zophia-pink">{tool.tag}</span>
              </div>
            </div>
            <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 rounded-full">
              <X size={18} />
            </button>
          </div>

          {renderContent()}
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
