import type { Metadata } from "next";
import { Inter } from "next/font/google";
import DarkModeSync from "../components/ui/DarkModeSync";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Tutor Agent",
  description: "An AI-powered Socratic tutor that learns from your notes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100`}>
        <DarkModeSync />
        {children}
      </body>
    </html>
  );
}
