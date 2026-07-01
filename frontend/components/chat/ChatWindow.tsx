"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import type { Message } from "../../lib/types";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onQuickStart?: (text: string) => void;
}

const SUGGESTIONS = [
  { icon: "📄", label: "Upload your notes", hint: "Drop a PDF, DOCX, or TXT on the left to get started." },
  { icon: "💬", label: "Explain a topic", text: "Explain photosynthesis to me" },
  { icon: "🧠", label: "Quiz me", text: "Quiz me on my notes" },
  { icon: "✅", label: "Check an answer", text: "Evaluate my answer: " },
];

export default function ChatWindow({ messages, isLoading, onQuickStart }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto flex max-w-2xl flex-col gap-3">
        {messages.length === 0 && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-10 flex flex-col items-center text-center"
          >
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 text-2xl shadow-lg shadow-indigo-500/30">
              🎓
            </div>
            <h2 className="text-lg font-semibold text-gray-100">How can I help you learn?</h2>
            <p className="mt-1 max-w-sm text-sm text-gray-500">
              Ask a question, upload your notes, or say &quot;quiz me&quot; to get started.
            </p>

            <div className="mt-6 grid w-full max-w-md grid-cols-1 gap-2 sm:grid-cols-2">
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion.label}
                  onClick={() => suggestion.text && onQuickStart?.(suggestion.text)}
                  className="flex items-center gap-2.5 rounded-xl border border-white/10 bg-white/[0.03] px-3.5 py-3 text-left text-sm text-gray-300 transition-colors hover:border-indigo-400/40 hover:bg-white/[0.06] hover:text-gray-100"
                >
                  <span className="text-base">{suggestion.icon}</span>
                  <span className="truncate">{suggestion.label}</span>
                </button>
              ))}
            </div>
          </motion.div>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
