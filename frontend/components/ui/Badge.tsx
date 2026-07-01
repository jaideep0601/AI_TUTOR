import type { BloomLevel } from "../../lib/types";

interface BadgeProps {
  level: BloomLevel;
  className?: string;
}

const levelClasses: Record<BloomLevel, string> = {
  remember: "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200",
  understand: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200",
  apply: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200",
  analyse: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-200",
  evaluate: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-200",
  create: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-200",
};

export default function Badge({ level, className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${levelClasses[level]} ${className}`}
    >
      {level}
    </span>
  );
}
