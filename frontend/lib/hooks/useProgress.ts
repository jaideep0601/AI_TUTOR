import useSWR from "swr";
import { fetchProgress } from "../api";
import { useTutorStore } from "../../stores/tutorStore";

export function useProgress() {
  const sessionId = useTutorStore((state) => state.sessionId);

  const { data, isLoading } = useSWR(
    sessionId ? ["progress", sessionId] : null,
    () => fetchProgress(sessionId),
    { refreshInterval: 10000 }
  );

  return { progress: data ?? null, isLoading };
}
