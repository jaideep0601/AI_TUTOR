"use client";

import { useEffect } from "react";
import { useTutorStore } from "../../stores/tutorStore";

export default function DarkModeSync() {
  const darkMode = useTutorStore((state) => state.darkMode);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return null;
}
