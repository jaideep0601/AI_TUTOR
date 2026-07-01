import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";
import type { Intent, Message, QuizQuestion } from "../lib/types";

interface TutorStore {
  sessionId: string;
  messages: Message[];
  mode: Intent;
  isLoading: boolean;
  quizQuestions: QuizQuestion[];
  currentQuiz: number;
  quizScores: number[];
  weakTopics: string[];
  uploadedFiles: string[];
  darkMode: boolean;
  setMode: (mode: Intent) => void;
  addMessage: (msg: Message) => void;
  setLoading: (v: boolean) => void;
  setQuiz: (q: QuizQuestion[]) => void;
  submitQuizAnswer: (score: number) => void;
  toggleDark: () => void;
  addUploadedFile: (filename: string) => void;
  setWeakTopics: (topics: string[]) => void;
}

export const useTutorStore = create<TutorStore>((set) => ({
  sessionId: uuidv4(),
  messages: [],
  mode: "ASK",
  isLoading: false,
  quizQuestions: [],
  currentQuiz: 0,
  quizScores: [],
  weakTopics: [],
  uploadedFiles: [],
  darkMode: true,

  setMode: (mode) => set({ mode }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setLoading: (v) => set({ isLoading: v }),
  setQuiz: (q) => set({ quizQuestions: q, currentQuiz: 0 }),
  submitQuizAnswer: (score) =>
    set((state) => ({
      quizScores: [...state.quizScores, score],
      currentQuiz: state.currentQuiz + 1,
    })),
  toggleDark: () => set((state) => ({ darkMode: !state.darkMode })),
  addUploadedFile: (filename) =>
    set((state) => ({ uploadedFiles: [...state.uploadedFiles, filename] })),
  setWeakTopics: (topics) => set({ weakTopics: topics }),
}));
