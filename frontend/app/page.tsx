"use client";

import Link from "next/link";
import { motion } from "framer-motion";

const FEATURES = [
  {
    title: "Upload your notes",
    description: "Drop in PDFs, DOCX, or TXT files and let the tutor learn your material.",
    icon: "📄",
    gradient: "from-indigo-500 to-blue-500",
    glow: "group-hover:shadow-indigo-500/40",
  },
  {
    title: "Ask & Learn",
    description: "Get Socratic, context-aware answers grounded in your own notes.",
    icon: "💬",
    gradient: "from-blue-500 to-cyan-500",
    glow: "group-hover:shadow-cyan-500/40",
  },
  {
    title: "Quiz yourself",
    description: "Auto-generated MCQs tagged by Bloom's taxonomy level.",
    icon: "🧠",
    gradient: "from-purple-500 to-indigo-500",
    glow: "group-hover:shadow-purple-500/40",
  },
  {
    title: "Track progress",
    description: "Visualize weak topics and quiz performance over time.",
    icon: "📈",
    gradient: "from-amber-500 to-orange-500",
    glow: "group-hover:shadow-amber-500/40",
  },
];

const STATS = [
  { value: "100%", label: "Free tier friendly" },
  { value: "6", label: "Bloom's levels tracked" },
  { value: "3", label: "File types supported" },
];

export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center overflow-hidden bg-[#05050f] bg-gradient-to-b from-[#0a0a1f] via-[#05050f] to-[#0a0612] px-6 py-24">
      <div
        className="pointer-events-none absolute inset-0 -z-20 opacity-[0.15]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #ffffff22 1px, transparent 1px), linear-gradient(to bottom, #ffffff22 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse 80% 60% at 50% 20%, black 40%, transparent 100%)",
        }}
      />

      <div className="pointer-events-none absolute inset-0 -z-10">
        <motion.div
          animate={{ x: [0, 40, 0], y: [0, -30, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
          className="absolute left-1/2 top-[-12%] h-[38rem] w-[38rem] -translate-x-1/2 rounded-full bg-indigo-600/30 blur-[130px]"
        />
        <motion.div
          animate={{ x: [0, -30, 0], y: [0, 25, 0] }}
          transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[-15%] right-[8%] h-96 w-96 rounded-full bg-purple-600/25 blur-[110px]"
        />
        <motion.div
          animate={{ x: [0, 25, 0], y: [0, 20, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[8%] left-[6%] h-72 w-72 rounded-full bg-cyan-500/15 blur-[100px]"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mx-auto max-w-2xl text-center"
      >
        <span className="mb-5 inline-flex items-center gap-2 rounded-full border border-indigo-400/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-medium text-indigo-300">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-indigo-400" />
          </span>
          Powered by Google Gemini
        </span>

        <div className="relative inline-block">
          <motion.span
            aria-hidden
            animate={{ opacity: [0.4, 0.8, 0.4], scale: [1, 1.05, 1] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="pointer-events-none absolute inset-0 -z-10 bg-indigo-500/40 blur-3xl"
          />
          <h1 className="relative text-5xl font-extrabold tracking-tight text-white [text-shadow:0_0_40px_rgba(129,140,248,0.6)] sm:text-7xl">
            AI Tutor Agent
            <motion.span
              aria-hidden
              animate={{ rotate: [0, 15, -10, 0], scale: [1, 1.15, 1] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -right-8 -top-2 text-3xl sm:-right-10 sm:text-4xl"
            >
              ✨
            </motion.span>
          </h1>
        </div>
        <p className="mx-auto mt-5 max-w-xl text-lg text-gray-400">
          A Socratic AI tutor that reads your notes, answers your questions, and quizzes
          you until it sticks.
        </p>

        <div className="mt-9 flex items-center justify-center gap-4">
          <Link
            href="/tutor"
            className="group relative inline-flex items-center gap-2 overflow-hidden rounded-lg bg-indigo-600 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-indigo-600/30 transition-all duration-200 hover:scale-[1.03] hover:bg-indigo-500 hover:shadow-xl hover:shadow-indigo-500/50"
          >
            <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
            Start Learning
            <span className="transition-transform duration-200 group-hover:translate-x-1">→</span>
          </Link>
        </div>

        <div className="mx-auto mt-14 grid max-w-md grid-cols-3 gap-4 border-t border-white/10 pt-8">
          {STATS.map((stat) => (
            <div key={stat.label}>
              <p className="bg-gradient-to-br from-white to-indigo-300 bg-clip-text text-2xl font-bold text-transparent">
                {stat.value}
              </p>
              <p className="mt-1 text-xs text-gray-500">{stat.label}</p>
            </div>
          ))}
        </div>
      </motion.div>

      <div className="mt-20 grid w-full max-w-3xl grid-cols-1 gap-4 sm:grid-cols-2">
        {FEATURES.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 + index * 0.08 }}
            whileHover={{ y: -4 }}
            className={`group relative overflow-hidden rounded-xl border border-white/10 bg-white/[0.03] p-5 text-left shadow-lg shadow-transparent backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:bg-white/[0.06] ${feature.glow}`}
          >
            <div
              className={`mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${feature.gradient} text-lg shadow-md transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3`}
            >
              {feature.icon}
            </div>
            <h3 className="text-sm font-semibold text-gray-100">{feature.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-gray-400">{feature.description}</p>
          </motion.div>
        ))}
      </div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="mt-16 text-xs text-gray-600"
      >
        No signup required for the demo · Your notes stay in your own session
      </motion.p>
    </main>
  );
}
