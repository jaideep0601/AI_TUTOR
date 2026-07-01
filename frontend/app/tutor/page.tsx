"use client";

import { useState } from "react";
import ChatWindow from "../../components/chat/ChatWindow";
import InputBar from "../../components/chat/InputBar";
import DropZone from "../../components/upload/DropZone";
import IngestionStatus from "../../components/upload/IngestionStatus";
import MaterialPanel from "../../components/upload/MaterialPanel";
import QuizCard from "../../components/quiz/QuizCard";
import ShortAnswerCard from "../../components/quiz/ShortAnswerCard";
import Sidebar from "../../components/sidebar/Sidebar";
import Button from "../../components/ui/Button";
import { useChat } from "../../lib/hooks/useChat";
import { useTutorStore } from "../../stores/tutorStore";
import type { IngestResponse } from "../../lib/types";

const MODE_LABELS: Record<string, string> = {
  ASK: "Ask",
  EXPLAIN: "Explain",
  QUIZ: "Quiz Me",
  EVALUATE: "Evaluate",
};

export default function TutorPage() {
  const { messages, sendMessage, isLoading } = useChat();
  const mode = useTutorStore((state) => state.mode);
  const sessionId = useTutorStore((state) => state.sessionId);
  const darkMode = useTutorStore((state) => state.darkMode);
  const toggleDark = useTutorStore((state) => state.toggleDark);
  const [ingestResults, setIngestResults] = useState<IngestResponse[]>([]);

  return (
    <div className="flex h-screen flex-col bg-gray-950 text-gray-100">
      <nav className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <h1 className="flex items-center gap-2 text-sm font-semibold">
          <span className="text-base">🎓</span> AI Tutor Agent
        </h1>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-white/5 px-2.5 py-1 text-xs text-gray-400">
            Session: {sessionId.slice(0, 8)}…
          </span>
          <Button variant="ghost" size="sm" onClick={toggleDark}>
            {darkMode ? "☀️ Light" : "🌙 Dark"}
          </Button>
        </div>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        <MaterialPanel>
          <div className="space-y-6">
            <div>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                Upload
              </h3>
              <DropZone onIngested={(result) => setIngestResults((prev) => [...prev, result])} />
              <IngestionStatus results={ingestResults} />
            </div>

            <div>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                Mode
              </h3>
              <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
                <span className="text-xs font-medium text-gray-200">
                  {MODE_LABELS[mode] ?? mode}
                </span>
              </div>
            </div>

            {mode === "QUIZ" && (
              <div>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Quiz
                </h3>
                <QuizCard />
              </div>
            )}
            {mode === "EVALUATE" && (
              <div>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Evaluate
                </h3>
                <ShortAnswerCard />
              </div>
            )}
          </div>
        </MaterialPanel>

        <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <ChatWindow messages={messages} isLoading={isLoading} onQuickStart={sendMessage} />
          <InputBar onSend={sendMessage} isLoading={isLoading} />
        </main>

        <Sidebar />
      </div>
    </div>
  );
}
