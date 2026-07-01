"use client";

import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import Badge from "../ui/Badge";
import type { Message } from "../../lib/types";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex w-full items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="mb-1 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 text-xs shadow-md">
          🎓
        </div>
      )}
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 shadow-sm ${
          isUser
            ? "rounded-br-md bg-gradient-to-br from-indigo-600 to-indigo-500 text-white"
            : "rounded-bl-md border border-white/10 bg-white/[0.05] text-gray-100"
        }`}
      >
        <div className="prose prose-sm prose-invert max-w-none prose-p:my-1 prose-pre:bg-black/30">
          <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{message.content}</ReactMarkdown>
        </div>
        {!isUser && message.bloomTags && message.bloomTags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {message.bloomTags.map((tag, index) => (
              <Badge key={`${tag}-${index}`} level={tag} />
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="mb-1 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-white/10 text-xs">
          🧑
        </div>
      )}
    </motion.div>
  );
}
