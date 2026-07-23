import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  Sparkles,
  CheckCircle2,
  Info,
  BookOpen,
  HelpCircle,
  FileText,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.sender === 'user';
  const [showAnalysis, setShowAnalysis] = useState(false);

  const analysis = message.analysis;

  const hasAnalysis =
    !isUser &&
    analysis &&
    typeof analysis === 'object' &&
    Object.keys(analysis).length > 0;

  const suggestions =
    analysis?.suggested_cares || analysis?.suggestions || [];

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 15,
        scale: 0.98,
      }}
      animate={{
        opacity: 1,
        y: 0,
        scale: 1,
      }}
      transition={{
        duration: 0.28,
        ease: [0.16, 1, 0.3, 1],
      }}
      className={`mx-auto my-3.5 flex max-w-3xl gap-3 ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-2xs ${
          isUser
            ? 'border border-slate-200 bg-slate-100 text-[11px] font-semibold text-slate-600'
            : 'border border-zophia-pink/30 bg-zophia-pink/15 p-1'
        }`}
      >
        {isUser ? (
          <span>Você</span>
        ) : (
          <img
            src="/zophia_mini_logo.png"
            onError={(event) => {
              event.currentTarget.onerror = null;
              event.currentTarget.src =
                '/assets/zophia_mini_logo.png';
            }}
            alt="Zophia"
            className="h-full w-full object-contain"
          />
        )}
      </div>

      {/* Conteúdo da mensagem */}
      <div
        className={`max-w-[85%] space-y-2.5 ${
          isUser ? 'items-end' : 'items-start'
        }`}
      >
        {/*
          O nome não é mais exibido aqui.
          O avatar já identifica quem enviou a mensagem.
          Isso remove a duplicação de "Zophia".
        */}

        <div
          className={`rounded-2xl p-4 text-sm leading-relaxed shadow-2xs ${
            isUser
              ? 'rounded-tr-xs bg-zophia-purple font-medium text-white'
              : message.isError
                ? 'rounded-tl-xs border border-red-200 bg-red-50 text-red-800'
                : 'rounded-tl-xs border border-zophia-border/80 bg-white text-zophia-text shadow-xs'
          }`}
        >
          <p className="whitespace-pre-wrap break-words">
            {message.text}
          </p>
        </div>

        {/* Análise estruturada */}
        {hasAnalysis && (
          <div className="w-full space-y-2.5">
            {analysis.risk_warning && (
              <div className="flex items-start gap-2.5 rounded-2xl border border-red-200 bg-red-50 p-3 text-red-900 shadow-2xs">
                <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />

                <div className="text-xs leading-relaxed">
                  <strong>Aviso de segurança:</strong>{' '}
                  {typeof analysis.risk_warning === 'string'
                    ? analysis.risk_warning
                    : 'Em situações de crise ou sofrimento intenso, procure apoio humano imediato e um serviço de emergência.'}
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={() =>
                setShowAnalysis((previousValue) => !previousValue)
              }
              aria-expanded={showAnalysis}
              className="flex items-center gap-2 rounded-xl border border-zophia-border bg-white px-3.5 py-2 text-xs font-semibold text-zophia-purple shadow-2xs transition-all duration-200 hover:border-zophia-pink/40 hover:shadow-xs"
            >
              <Sparkles
                size={14}
                className="text-zophia-pink"
              />

              <span>
                {showAnalysis
                  ? 'Ocultar análise estruturada'
                  : 'Ver análise estruturada'}
              </span>

              {showAnalysis ? (
                <ChevronUp size={14} />
              ) : (
                <ChevronDown size={14} />
              )}
            </button>

            <AnimatePresence initial={false}>
              {showAnalysis && (
                <motion.div
                  initial={{
                    opacity: 0,
                    height: 0,
                  }}
                  animate={{
                    opacity: 1,
                    height: 'auto',
                  }}
                  exit={{
                    opacity: 0,
                    height: 0,
                  }}
                  transition={{
                    duration: 0.2,
                  }}
                  className="space-y-2.5 overflow-hidden pt-1"
                >
                  {/* Resumo acolhedor */}
                  {(analysis.welcoming_summary ||
                    analysis.summary) && (
                    <div className="space-y-1 rounded-2xl border border-zophia-purple/20 bg-zophia-sidebar p-3.5 shadow-2xs">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-zophia-purple">
                          <Sparkles
                            size={14}
                            className="text-zophia-pink"
                          />

                          <span>Resumo acolhedor</span>
                        </div>

                        <span className="rounded-md bg-zophia-purple/10 px-2 py-0.5 text-[9px] font-semibold text-zophia-purple">
                          IA
                        </span>
                      </div>

                      <p className="text-xs font-medium leading-relaxed text-slate-700">
                        {analysis.welcoming_summary ||
                          analysis.summary}
                      </p>
                    </div>
                  )}

                  {/* Sinais observados */}
                  {Array.isArray(analysis.signs) &&
                    analysis.signs.length > 0 && (
                      <div className="space-y-2 rounded-2xl border border-zophia-border bg-white p-3.5 shadow-2xs">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                          <Info
                            size={14}
                            className="text-zophia-purple"
                          />

                          <span>Sinais observados</span>
                        </div>

                        <div className="flex flex-wrap gap-1.5">
                          {analysis.signs.map((sign, index) => (
                            <span
                              key={`${sign}-${index}`}
                              className="rounded-full border border-zophia-purple/15 bg-zophia-purple/10 px-2.5 py-0.5 text-xs font-medium text-zophia-purple"
                            >
                              {sign}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* Informações educativas */}
                  {analysis.educational_info && (
                    <div className="space-y-1 rounded-2xl border border-zophia-border bg-white p-3.5 shadow-2xs">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                        <BookOpen
                          size={14}
                          className="text-zophia-purple"
                        />

                        <span>Informações educativas</span>
                      </div>

                      <p className="text-xs font-normal leading-relaxed text-slate-600">
                        {analysis.educational_info}
                      </p>
                    </div>
                  )}

                  {/* Cuidados sugeridos */}
                  {Array.isArray(suggestions) &&
                    suggestions.length > 0 && (
                      <div className="space-y-1.5 rounded-2xl border border-zophia-border bg-white p-3.5 shadow-2xs">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900">
                          <CheckCircle2
                            size={14}
                            className="shrink-0 text-emerald-600"
                          />

                          <span>Cuidados sugeridos</span>
                        </div>

                        <ul className="space-y-1">
                          {suggestions.map(
                            (suggestion, index) => (
                              <li
                                key={`${suggestion}-${index}`}
                                className="flex items-start gap-2 text-xs font-medium leading-relaxed text-slate-700"
                              >
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />

                                <span>{suggestion}</span>
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {/* Quando procurar ajuda */}
                  {analysis.when_to_seek_help && (
                    <div className="space-y-1 rounded-2xl border border-zophia-border bg-white p-3.5 shadow-2xs">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                        <HelpCircle
                          size={14}
                          className="shrink-0 text-amber-600"
                        />

                        <span>
                          Quando procurar ajuda profissional
                        </span>
                      </div>

                      <p className="text-xs font-normal leading-relaxed text-slate-600">
                        {analysis.when_to_seek_help}
                      </p>
                    </div>
                  )}

                  {/* Fontes */}
                  {Array.isArray(analysis.sources) &&
                    analysis.sources.length > 0 && (
                      <div className="space-y-1 rounded-2xl border border-slate-200/80 bg-slate-50/70 p-3">
                        <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-700">
                          <FileText
                            size={13}
                            className="text-zophia-purple"
                          />

                          <span>Fontes utilizadas:</span>
                        </div>

                        <ul className="list-disc space-y-0.5 pl-4 text-[11px] text-slate-600">
                          {analysis.sources.map(
                            (source, index) => (
                              <li
                                key={`${source}-${index}`}
                              >
                                {source}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {/* Aviso educacional */}
                  <div className="flex items-center gap-2 rounded-2xl border border-zophia-border bg-zophia-bg p-2.5 text-[11px] leading-relaxed text-slate-500">
                    <ShieldAlert
                      size={14}
                      className="shrink-0 text-zophia-pink"
                    />

                    <span>
                      {analysis.safety_notice ||
                        'A Zophia é uma ferramenta educacional e não substitui atendimento médico ou psicológico.'}
                    </span>
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