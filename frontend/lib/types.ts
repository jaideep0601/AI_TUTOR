export type Intent = "ASK" | "EXPLAIN" | "QUIZ" | "EVALUATE";

export type BloomLevel =
  | "remember"
  | "understand"
  | "apply"
  | "analyse"
  | "evaluate"
  | "create";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: Intent;
  bloomTags?: BloomLevel[];
  timestamp: Date;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
  explanation: string;
  bloom_level: BloomLevel;
}

export interface EvaluationResult {
  correct: boolean;
  score: number;
  feedback: string;
  correct_answer: string;
}

export interface ProgressData {
  topics_covered: string[];
  weak_topics: string[];
  quiz_scores: number[];
  bloom_distribution: Record<BloomLevel, number>;
}

export interface ChatResponse {
  response: string;
  intent: Intent;
  bloom_tags: BloomLevel[];
}

export interface IngestResponse {
  chunks_stored: number;
  filename: string;
}

export type ChatApiResult =
  | ChatResponse
  | { questions: QuizQuestion[] }
  | EvaluationResult;
