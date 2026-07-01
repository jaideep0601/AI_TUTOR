"use client";

import { useState } from "react";
import { sendMessage, isEvaluationResult } from "../../lib/api";
import { useTutorStore } from "../../stores/tutorStore";
import type { EvaluationResult } from "../../lib/types";
import Button from "../ui/Button";
import ScoreDisplay from "./ScoreDisplay";

export default function ShortAnswerCard() {
  const sessionId = useTutorStore((state) => state.sessionId);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!answer.trim()) return;
    setIsSubmitting(true);
    try {
      const response = await sendMessage(sessionId, `Evaluate my answer: ${answer}`);
      if (isEvaluationResult(response)) {
        setResult(response);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-3">
      <textarea
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Type your answer..."
        rows={4}
        className="w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 outline-none focus:border-indigo-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
      />
      <Button onClick={handleSubmit} disabled={isSubmitting || !answer.trim()}>
        {isSubmitting ? "Grading..." : "Submit Answer"}
      </Button>
      {result && <ScoreDisplay result={result} />}
    </div>
  );
}
