"use client";

import { useRef, useState, type KeyboardEvent } from "react";
import { useTutorStore } from "../../stores/tutorStore";
import type { Intent } from "../../lib/types";

interface InputBarProps {
  onSend: (text: string) => void;
  isLoading: boolean;
}

const MODES: { label: string; value: Intent; icon: string }[] = [
  { label: "Ask", value: "ASK", icon: "💬" },
  { label: "Explain", value: "EXPLAIN", icon: "📖" },
  { label: "Quiz Me", value: "QUIZ", icon: "🧠" },
  { label: "Evaluate", value: "EVALUATE", icon: "✅" },
];

export default function InputBar({ onSend, isLoading }: InputBarProps) {
  const [text, setText] = useState("");
  const mode = useTutorStore((state) => state.mode);
  const setMode = useTutorStore((state) => state.setMode);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!text.trim() || isLoading) return;
    onSend(text);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(event.target.value);
    const el = event.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 4 * 24)}px`;
  };

  return (
    <div className="border-t border-white/10 bg-gray-950/80 px-4 py-3 backdrop-blur">
      <div className="mx-auto flex max-w-2xl flex-col gap-2.5">
        <div className="flex gap-1.5">
          {MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => setMode(m.value)}
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all duration-150 ${
                mode === m.value
                  ? "bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-600/30"
                  : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-gray-200"
              }`}
            >
              <span>{m.icon}</span>
              {m.label}
            </button>
          ))}
        </div>
        <div className="flex items-end gap-2 rounded-2xl border border-white/10 bg-white/[0.04] p-1.5 pl-4 transition-colors focus-within:border-indigo-400/50 focus-within:bg-white/[0.06]">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            placeholder="Type your message..."
            className="max-h-24 flex-1 resize-none bg-transparent py-2 text-sm text-gray-100 outline-none placeholder:text-gray-500 disabled:opacity-60"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !text.trim()}
            aria-label="Send message"
            className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all duration-150 hover:scale-105 hover:shadow-indigo-500/50 disabled:cursor-not-allowed disabled:scale-100 disabled:from-gray-700 disabled:to-gray-700 disabled:text-gray-500 disabled:shadow-none"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
