"use client";

import {
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useProgress } from "../../lib/hooks/useProgress";
import Skeleton from "../ui/Skeleton";
import TopicBadge from "./TopicBadge";

const BLOOM_LEVELS = ["remember", "understand", "apply", "analyse", "evaluate", "create"] as const;

export default function ProgressPanel() {
  const { progress, isLoading } = useProgress();

  if (isLoading && !progress) {
    return (
      <div className="space-y-3 p-4">
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!progress) {
    return <p className="p-4 text-xs text-gray-400">No progress data yet.</p>;
  }

  const radarData = BLOOM_LEVELS.map((level) => ({
    level,
    value: progress.bloom_distribution[level] ?? 0,
  }));

  const lineData = progress.quiz_scores.map((score, index) => ({
    attempt: index + 1,
    score,
  }));

  return (
    <div className="space-y-6 p-4">
      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Bloom&apos;s Taxonomy Coverage
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="level" tick={{ fontSize: 10 }} />
            <Radar dataKey="value" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.4} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Quiz Scores
        </h3>
        {lineData.length > 0 ? (
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={lineData}>
              <XAxis dataKey="attempt" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 10]} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#4f46e5" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-xs text-gray-400">No quiz attempts yet.</p>
        )}
      </div>

      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Weak Topics
        </h3>
        <div className="space-y-1.5">
          {progress.weak_topics.length === 0 && (
            <p className="text-xs text-gray-400">None identified yet.</p>
          )}
          {progress.weak_topics.map((topic, index) => (
            <TopicBadge key={index} label={topic} isWeak level="apply" />
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Topics Covered
        </h3>
        <div className="space-y-1.5">
          {progress.topics_covered.length === 0 && (
            <p className="text-xs text-gray-400">Upload notes to get started.</p>
          )}
          {progress.topics_covered.map((topic, index) => (
            <TopicBadge key={index} label={topic} level="understand" />
          ))}
        </div>
      </div>
    </div>
  );
}
