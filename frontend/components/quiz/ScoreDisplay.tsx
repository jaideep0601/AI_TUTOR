import type { EvaluationResult } from "../../lib/types";

interface ScoreDisplayProps {
  result: EvaluationResult;
}

export default function ScoreDisplay({ result }: ScoreDisplayProps) {
  const colorClass =
    result.score < 5
      ? "text-red-600 dark:text-red-400"
      : result.score <= 7
      ? "text-amber-600 dark:text-amber-400"
      : "text-green-600 dark:text-green-400";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center gap-3">
        <span className={`text-2xl font-bold ${colorClass}`}>{result.score}/10</span>
        <span className={result.correct ? "text-green-600" : "text-red-600"}>
          {result.correct ? "✓ Correct" : "✗ Incorrect"}
        </span>
      </div>
      <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{result.feedback}</p>
      <p className="mt-2 text-xs text-gray-400">
        <span className="font-medium">Correct answer:</span> {result.correct_answer}
      </p>
    </div>
  );
}
