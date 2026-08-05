import React from 'react';
import { motion } from 'framer-motion';

export default function ToolCard({ icon: Icon, title, description, tag, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full p-3.5 rounded-2xl bg-white border border-zophia-border hover:border-zophia-purple/30 shadow-2xs hover:shadow-xs transition-all text-left flex items-start gap-3 group"
    >
      <div className="p-2.5 rounded-xl bg-zophia-bg text-zophia-purple group-hover:bg-zophia-purple group-hover:text-white transition-colors shrink-0">
        <Icon size={18} />
      </div>

      <div className="space-y-0.5 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <h4 className="font-heading font-semibold text-xs text-zophia-text truncate group-hover:text-zophia-purple transition-colors">
            {title}
          </h4>
          {tag && (
            <span className="text-[9px] font-bold text-zophia-purple bg-zophia-purple/5 px-1.5 py-0.5 rounded-md shrink-0">
              {tag}
            </span>
          )}
        </div>
        <p className="text-[11px] text-gray-500 line-clamp-2 leading-relaxed">
          {description}
        </p>
      </div>
    </motion.button>
  );
}
