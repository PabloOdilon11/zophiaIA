import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, isLoading }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSendMessage(text.trim());
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="sticky bottom-0 bg-zophia-bg pt-3 pb-5 px-4">
      <form 
        onSubmit={handleSubmit}
        className="max-w-3xl mx-auto relative flex items-center bg-white rounded-[28px] border border-zophia-border shadow-sm hover:shadow-md focus-within:border-zophia-pink/60 focus-within:ring-4 focus-within:ring-zophia-pink/10 transition-all duration-200"
      >
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escreva sua mensagem para a Zophia..."
          rows={1}
          disabled={isLoading}
          className="w-full resize-none bg-transparent py-4 pl-6 pr-14 text-sm text-zophia-text placeholder:text-gray-400 focus:outline-none max-h-36 font-body leading-relaxed"
        />

        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          className={`absolute right-3 p-2.5 rounded-full transition-all duration-200 ${
            text.trim() && !isLoading
              ? 'bg-zophia-purple text-white shadow-sm hover:bg-zophia-purple/90 hover:scale-105 active:scale-95'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
        >
          {isLoading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
        </button>
      </form>
      <p className="text-[11px] text-center text-gray-400 mt-2 font-medium">
        Pressione Enter para enviar • Shift + Enter para quebra de linha
      </p>
    </div>
  );
}
