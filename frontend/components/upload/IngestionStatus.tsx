"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { IngestResponse } from "../../lib/types";

interface IngestionStatusProps {
  results: IngestResponse[];
}

export default function IngestionStatus({ results }: IngestionStatusProps) {
  if (results.length === 0) return null;

  return (
    <AnimatePresence>
      <div className="mt-3 space-y-2">
        {results.map((result, index) => (
          <motion.div
            key={`${result.filename}-${index}`}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.25 }}
            className="flex items-center justify-between gap-2 rounded-lg border border-green-500/20 bg-green-500/10 px-3 py-2 text-xs"
          >
            <span className="flex min-w-0 items-center gap-1.5 truncate text-gray-200">
              <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full bg-green-500/20 text-[10px] text-green-400">
                ✓
              </span>
              <span className="truncate">{result.filename}</span>
            </span>
            <span className="flex-shrink-0 text-green-400">{result.chunks_stored} chunks</span>
          </motion.div>
        ))}
      </div>
    </AnimatePresence>
  );
}
