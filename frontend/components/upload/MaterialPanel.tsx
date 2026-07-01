"use client";

import { useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";

interface MaterialPanelProps {
  children: ReactNode;
}

export default function MaterialPanel({ children }: MaterialPanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="relative flex-shrink-0">
      <AnimatePresence initial={false} mode="wait">
        {isOpen ? (
          <motion.div
            key="open"
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="h-full overflow-hidden border-r border-white/10 bg-white/[0.02] dark:border-gray-800"
          >
            <div className="h-full w-[280px] overflow-y-auto">
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 dark:border-gray-800">
                <h2 className="flex items-center gap-1.5 text-sm font-semibold text-gray-100">
                  <span>📚</span> Study Material
                </h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-md px-1.5 py-1 text-xs text-gray-500 transition-colors hover:bg-white/10 hover:text-gray-200"
                  aria-label="Hide study material panel"
                >
                  ‹
                </button>
              </div>
              <div className="p-4">{children}</div>
            </div>
          </motion.div>
        ) : (
          <motion.button
            key="closed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => setIsOpen(true)}
            aria-label="Show study material panel"
            className="flex h-full w-9 flex-col items-center justify-center gap-3 border-r border-white/10 bg-white/[0.02] text-gray-500 transition-colors hover:bg-white/[0.05] hover:text-indigo-300 dark:border-gray-800"
          >
            <span className="text-sm">›</span>
            <span className="text-base">📚</span>
            <span className="[writing-mode:vertical-rl] text-[10px] font-medium uppercase tracking-wide">
              Study Material
            </span>
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
