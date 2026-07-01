"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import ProgressPanel from "./ProgressPanel";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="relative flex-shrink-0">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="absolute -left-6 top-4 z-10 rounded-l-lg border border-r-0 border-gray-200 bg-white px-1.5 py-2 text-xs text-gray-500 dark:border-gray-800 dark:bg-gray-900"
      >
        {isOpen ? "›" : "‹"}
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: 320 }}
            exit={{ width: 0 }}
            transition={{ duration: 0.25 }}
            className="h-full overflow-hidden border-l border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900"
          >
            <div className="w-80 h-full overflow-y-auto">
              <h2 className="border-b border-gray-200 px-4 py-3 text-sm font-semibold text-gray-800 dark:border-gray-800 dark:text-gray-100">
                Progress
              </h2>
              <ProgressPanel />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
