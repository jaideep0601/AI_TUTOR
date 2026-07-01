import { useCallback, useMemo, useState } from "react";
import { useTutorStore } from "../../stores/tutorStore";

export function useQuiz() {
  const quizQuestions = useTutorStore((state) => state.quizQuestions);
  const currentQuiz = useTutorStore((state) => state.currentQuiz);
  const submitQuizAnswer = useTutorStore((state) => state.submitQuizAnswer);
  const quizScores = useTutorStore((state) => state.quizScores);

  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);

  const currentQ = useMemo(() => quizQuestions[currentQuiz] ?? null, [quizQuestions, currentQuiz]);

  const selectAnswer = useCallback(
    (option: string) => {
      if (revealed || !currentQ) return;
      setSelectedOption(option);
      setRevealed(true);
    },
    [revealed, currentQ]
  );

  const next = useCallback(() => {
    if (!currentQ) return;
    const isCorrect = selectedOption === currentQ.answer;
    submitQuizAnswer(isCorrect ? 10 : 0);
    setSelectedOption(null);
    setRevealed(false);
  }, [currentQ, selectedOption, submitQuizAnswer]);

  const score = useMemo(
    () => (quizScores.length ? Math.round(quizScores.reduce((a, b) => a + b, 0) / quizScores.length) : 0),
    [quizScores]
  );

  return {
    currentQ,
    currentIndex: currentQuiz,
    total: quizQuestions.length,
    selectedOption,
    selectAnswer,
    revealed,
    score,
    next,
  };
}
