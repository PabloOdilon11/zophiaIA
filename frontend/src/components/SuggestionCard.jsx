import React from 'react';
import { motion } from 'framer-motion';

export default function SuggestionCard({ icon: Icon, title, description, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full min-h-[100px] p-4 rounded-2xl bg-white border border-zophia-border hover:border-zophia-pink/50 shadow-xs hover:shadow-md transition-all duration-200 text-left flex flex-col justify-between group focus:outline-none focus:ring-2 focus:ring-zophia-pink/30"
    >
      <div className="p-2 rounded-xl bg-zophia-bg w-fit text-zophia-purple group-hover:bg-zophia-pink/10 group-hover:text-zophia-pink transition-colors shrink-0">
        <Icon size={18} />
      </div>
      <div className="mt-2">
        <h4 className="font-heading font-bold text-sm text-slate-800 group-hover:text-zophia-purple transition-colors leading-snug">{title}</h4>
        {description && <p className="text-xs text-slate-600 mt-1 leading-relaxed">{description}</p>}
      </div>
    </motion.button>
  );
}
