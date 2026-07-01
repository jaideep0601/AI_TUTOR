import type { BloomLevel } from "../../lib/types";
import Badge from "../ui/Badge";

interface TopicBadgeProps {
  label: string;
  level?: BloomLevel;
  isWeak?: boolean;
}

export default function TopicBadge({ label, level = "understand", isWeak = false }: TopicBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      {isWeak && <span className="h-2 w-2 flex-shrink-0 rounded-full bg-red-500" />}
      <span className="truncate text-xs text-gray-600 dark:text-gray-300">{label}</span>
      <Badge level={level} className="ml-auto flex-shrink-0" />
    </div>
  );
}
