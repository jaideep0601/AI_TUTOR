"use client";

import { AnimatePresence, motion } from "framer-motion";
import Badge from "../ui/Badge";
import Button from "../ui/Button";
import { useQuiz } from "../../lib/hooks/useQuiz";

export default function QuizCard() {
  const { currentQ, currentIndex, total, selectedOption, selectAnswer, revealed, next } = useQuiz();

  if (!currentQ) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-6 text-center text-sm text-gray-400 dark:border-gray-800 dark:bg-gray-900">
        No quiz active. Say &quot;quiz me&quot; in the chat to generate one.
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentIndex}
        initial={{ rotateY: 90, opacity: 0 }}
        animate={{ rotateY: 0, opacity: 1 }}
        exit={{ rotateY: -90, opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"
      >
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs text-gray-400">
            Question {currentIndex + 1} of {total}
          </span>
          <Badge level={currentQ.bloom_level} />
        </div>
        <p className="mb-4 text-sm font-medium text-gray-900 dark:text-gray-100">{currentQ.question}</p>
        <div className="space-y-2">
          {currentQ.options.map((option) => {
            const isSelected = selectedOption === option;
            const isCorrectOption = option === currentQ.answer;
            let optionClasses =
              "w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors border-gray-200 dark:border-gray-700";

            if (revealed) {
              if (isCorrectOption) {
                optionClasses += " bg-green-50 border-green-400 text-green-700 dark:bg-green-950 dark:text-green-300";
              } else if (isSelected) {
                optionClasses += " bg-red-50 border-red-400 text-red-700 dark:bg-red-950 dark:text-red-300";
              } else {
                optionClasses += " opacity-60";
              }
            } else {
              optionClasses += " hover:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950";
            }

            return (
              <button
                key={option}
                onClick={() => selectAnswer(option)}
                disabled={revealed}
                className={optionClasses}
              >
                {option}
              </button>
            );
          })}
        </div>
        {revealed && (
          <div className="mt-4 rounded-lg bg-gray-50 p-3 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-300">
            {currentQ.explanation}
          </div>
        )}
        {revealed && (
          <Button className="mt-4 w-full" onClick={next}>
            Next
          </Button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
