import type {
  ChatApiResult,
  EvaluationResult,
  IngestResponse,
  ProgressData,
  QuizQuestion,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, sessionId: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "X-Session-Id": sessionId,
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(text || response.statusText, response.status);
  }

  return response.json() as Promise<T>;
}

export function isEvaluationResult(result: ChatApiResult): result is EvaluationResult {
  return "correct" in result && "score" in result;
}

export function isQuizResult(result: ChatApiResult): result is { questions: QuizQuestion[] } {
  return "questions" in result;
}

export async function sendMessage(sessionId: string, message: string): Promise<ChatApiResult> {
  return request<ChatApiResult>("/chat", sessionId, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
}

export async function uploadFile(sessionId: string, file: File): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("session_id", sessionId);

  return request<IngestResponse>("/ingest", sessionId, {
    method: "POST",
    body: formData,
  });
}

export async function generateQuiz(sessionId: string): Promise<QuizQuestion[]> {
  const result = await request<{ questions: QuizQuestion[] }>(
    `/quiz?session_id=${encodeURIComponent(sessionId)}`,
    sessionId,
    { method: "GET" }
  );
  return result.questions;
}

export async function fetchProgress(sessionId: string): Promise<ProgressData> {
  return request<ProgressData>(
    `/progress?session_id=${encodeURIComponent(sessionId)}`,
    sessionId,
    { method: "GET" }
  );
}
