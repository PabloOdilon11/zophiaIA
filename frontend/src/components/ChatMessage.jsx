import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Sparkles, CheckCircle2, Info, BookOpen, HelpCircle, FileText, ChevronDown, ChevronUp } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.sender === 'user';
  const [showAnalysis, setShowAnalysis] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
      className={`flex gap-3 max-w-3xl mx-auto my-3.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-2xs ${isUser
          ? 'bg-slate-100 border border-slate-200 text-slate-600 font-semibold text-[11px]'
          : 'bg-zophia-pink/15 p-1 border border-zophia-pink/30 shadow-2xs'
        }`}>
        {isUser ? 'Você' : (
          <img
            src="/zophia_mini_logo.png"
            onError={(e) => { e.target.src = '/assets/zophia_mini_logo.png'; }}
            alt="Zophia"
            className="w-full h-full object-contain"
          />
        )}
      </div>

      {/* Message Content */}
      <div className={`space-y-2.5 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`text-[11px] font-semibold px-1 text-gray-400 ${isUser ? 'text-right' : 'text-left'}`}>
          {isUser ? 'Você' : 'Zophia'}
        </div>

        {/* Clean Conversational Chat Bubble */}
        <div className={`p-4 rounded-2xl leading-relaxed text-sm shadow-2xs ${isUser
            ? 'bg-zophia-purple text-white rounded-tr-xs font-medium'
            : 'bg-white border border-zophia-border/80 text-zophia-text rounded-tl-xs shadow-xs'
          }`}>
          {message.text}
        </div>

        {/* Option A: Discretely Toggleable Structured Analysis & RAG Button */}
        {!isUser && message.analysis && (
          <div className="space-y-2.5 w-full">
            {message.analysis.risk_warning && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-900 rounded-2xl flex items-start gap-2.5 shadow-2xs">
                <ShieldAlert className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                <div className="text-xs leading-relaxed">
                  <strong>Aviso de Segurança:</strong> Em situações de crise ou sofrimento intenso, busque apoio emergencial ou o serviço CVV (Ligue 188).
                </div>
              </div>
            )}

            <button
              onClick={() => setShowAnalysis(!showAnalysis)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-zophia-border hover:border-zophia-pink/40 text-zophia-purple text-xs font-semibold shadow-2xs hover:shadow-xs transition-all duration-200"
            >
              <Sparkles size={14} className="text-zophia-pink" />
              <span>{showAnalysis ? 'Ocultar Análise Estruturada & Embasamento RAG' : 'Ver Análise Estruturada & Embasamento RAG'}</span>
              {showAnalysis ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            <AnimatePresence>
              {showAnalysis && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-2.5 overflow-hidden pt-1"
                >
                  {/* 1. Resumo Acolhedor */}
                  <div className="p-3.5 bg-zophia-sidebar rounded-2xl border border-zophia-purple/20 space-y-1 shadow-2xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-zophia-purple font-heading font-bold text-xs">
                        <Sparkles size={14} className="text-zophia-pink" />
                        <span>Resumo Acolhedor</span>
                      </div>
                      <span className="text-[9px] font-semibold text-zophia-purple bg-zophia-purple/10 px-2 py-0.5 rounded-md">RAG: LLM</span>
                    </div>
                    <p className="text-xs text-slate-700 leading-relaxed font-medium">
                      {message.analysis.welcoming_summary || message.analysis.summary}
                    </p>
                  </div>

                  {/* 2. Sinais Observados */}
                  {message.analysis.signs && message.analysis.signs.length > 0 && (
                    <div className="p-3.5 bg-white rounded-2xl border border-zophia-border space-y-2 shadow-2xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                          <Info size={14} className="text-zophia-purple" />
                          <span>Sinais Observados</span>
                        </div>
                        <span className="text-[9px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">RAG: DSM-5-TR</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {message.analysis.signs.map((sign, i) => (
                          <span key={i} className="text-xs text-zophia-purple bg-zophia-purple/10 px-2.5 py-0.5 rounded-full font-medium border border-zophia-purple/15">
                            {sign}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 3. Informações Educativas */}
                  {message.analysis.educational_info && (
                    <div className="p-3.5 bg-white rounded-2xl border border-zophia-border space-y-1 shadow-2xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                          <BookOpen size={14} className="text-zophia-purple" />
                          <span>Informações Educativas</span>
                        </div>
                        <span className="text-[9px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">RAG: DSM-5-TR / NICE</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed font-normal">
                        {message.analysis.educational_info}
                      </p>
                    </div>
                  )}

                  {/* 4. Cuidados Sugeridos */}
                  {((message.analysis.suggested_cares && message.analysis.suggested_cares.length > 0) || (message.analysis.suggestions && message.analysis.suggestions.length > 0)) && (
                    <div className="p-3.5 bg-white rounded-2xl border border-zophia-border space-y-1.5 shadow-2xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900">
                          <CheckCircle2 size={14} className="text-emerald-600 shrink-0" />
                          <span>Cuidados Sugeridos</span>
                        </div>
                        <span className="text-[9px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">RAG: WHO mhGAP / NICE</span>
                      </div>
                      <ul className="space-y-1">
                        {(message.analysis.suggested_cares || message.analysis.suggestions).map((sug, i) => (
                          <li key={i} className="text-xs text-slate-700 flex items-start gap-2 font-medium leading-relaxed">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0 mt-1.5"></span>
                            <span>{sug}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 5. Quando Procurar Ajuda Profissional */}
                  {message.analysis.when_to_seek_help && (
                    <div className="p-3.5 bg-white rounded-2xl border border-zophia-border space-y-1 shadow-2xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                          <HelpCircle size={14} className="text-amber-600 shrink-0" />
                          <span>Quando Procurar Ajuda Profissional</span>
                        </div>
                        <span className="text-[9px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md">RAG: mhGAP / RAPS</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed font-normal">
                        {message.analysis.when_to_seek_help}
                      </p>
                    </div>
                  )}

                  {/* 6. Fontes Utilizadas */}
                  {message.analysis.sources && message.analysis.sources.length > 0 && (
                    <div className="p-3 bg-slate-50/70 rounded-2xl border border-slate-200/80 space-y-1">
                      <div className="text-[11px] font-bold text-slate-700 flex items-center gap-1.5">
                        <FileText size={13} className="text-zophia-purple" />
                        <span>Fontes utilizadas (Base Documental RAG):</span>
                      </div>
                      <ul className="text-[11px] text-slate-600 space-y-0.5 pl-4 list-disc">
                        {message.analysis.sources.map((src, i) => (
                          <li key={i}>{src}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 7. Aviso de Segurança */}
                  <div className="p-2.5 bg-zophia-bg rounded-2xl border border-zophia-border text-[11px] text-slate-500 leading-relaxed flex items-center gap-2">
                    <ShieldAlert size={14} className="text-zophia-pink shrink-0" />
                    <span>{message.analysis.safety_notice || "A Zophia é uma ferramenta educacional e não substitui atendimento médico ou psicológico."}</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  );
}
