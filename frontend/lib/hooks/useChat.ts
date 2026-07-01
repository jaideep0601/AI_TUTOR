import { useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import { isEvaluationResult, isQuizResult, sendMessage } from "../api";
import { useTutorStore } from "../../stores/tutorStore";
import type { EvaluationResult } from "../types";

export function useChat() {
  const messages = useTutorStore((state) => state.messages);
  const isLoading = useTutorStore((state) => state.isLoading);
  const sessionId = useTutorStore((state) => state.sessionId);
  const addMessage = useTutorStore((state) => state.addMessage);
  const setLoading = useTutorStore((state) => state.setLoading);
  const setQuiz = useTutorStore((state) => state.setQuiz);

  const formatEvaluation = (evaluation: EvaluationResult): string => {
    return `**Score: ${evaluation.score}/10** — ${evaluation.correct ? "Correct" : "Needs work"}\n\n${evaluation.feedback}\n\n**Correct answer:** ${evaluation.correct_answer}`;
  };

  const sendUserMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      addMessage({
        id: uuidv4(),
        role: "user",
        content: text,
        timestamp: new Date(),
      });

      setLoading(true);
      try {
        const result = await sendMessage(sessionId, text);

        if (isQuizResult(result)) {
          setQuiz(result.questions);
          addMessage({
            id: uuidv4(),
            role: "assistant",
            content: `I've generated ${result.questions.length} quiz questions for you. Check the quiz panel to get started!`,
            intent: "QUIZ",
            timestamp: new Date(),
          });
        } else if (isEvaluationResult(result)) {
          addMessage({
            id: uuidv4(),
            role: "assistant",
            content: formatEvaluation(result),
            intent: "EVALUATE",
            timestamp: new Date(),
          });
        } else {
          addMessage({
            id: uuidv4(),
            role: "assistant",
            content: result.response,
            intent: result.intent,
            bloomTags: result.bloom_tags,
            timestamp: new Date(),
          });
        }
      } catch (error) {
        addMessage({
          id: uuidv4(),
          role: "assistant",
          content: "Sorry, something went wrong reaching the tutor. Please try again.",
          timestamp: new Date(),
        });
      } finally {
        setLoading(false);
      }
    },
    [addMessage, setLoading, setQuiz, sessionId]
  );

  return { messages, sendMessage: sendUserMessage, isLoading };
}
