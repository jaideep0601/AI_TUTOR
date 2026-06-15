"""
main.py
───────
CLI entry point for the AI Tutor Agent.

Usage:
  python main.py ingest --path ./docs
  python main.py ingest --file lecture_notes.pdf
  python main.py chat
  python main.py stats
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_ingest(args: argparse.Namespace) -> None:
    from ingest.pipeline import ingest_file, ingest_directory, get_kb_stats

    if args.file:
        result = ingest_file(args.file)
        print(f"✅  {result['source']}")
        print(f"    Sections loaded : {result['sections_loaded']}")
        print(f"    Chunks created  : {result['chunks_created']}")
        print(f"    New chunks added: {result['chunks_ingested']}")
    elif args.path:
        results = ingest_directory(args.path)
        total_new = sum(r["chunks_ingested"] for r in results)
        print(f"\n✅  {len(results)} file(s) processed — {total_new} new chunks added.")
        for r in results:
            print(f"    • {r['source']}: {r['chunks_ingested']} new chunks")
    else:
        print("❌  Provide --file or --path")
        sys.exit(1)

    stats = get_kb_stats()
    print(f"\n📚 KB now has {stats['total_chunks']} total chunks across "
          f"{len(stats['unique_sources'])} source(s).")


def cmd_stats(args: argparse.Namespace) -> None:
    from ingest.pipeline import get_kb_stats

    stats = get_kb_stats()
    print(f"📚 Knowledge Base Stats")
    print(f"   Total chunks  : {stats['total_chunks']}")
    print(f"   Unique sources: {len(stats['unique_sources'])}")
    if stats["unique_sources"]:
        for src in stats["unique_sources"]:
            print(f"     • {src}")


def cmd_chat(args: argparse.Namespace) -> None:
    """Simple REPL for terminal-based testing (no Streamlit)."""
    from agents.graph import run_tutor
    from agents.state import TutorState

    print("🎓 AI Tutor — Terminal Mode")
    print("   Type 'quit' to exit, 'quiz' to request a quiz.\n")

    state: TutorState = {
        "session_topics": [],
        "weak_topics": [],
        "quiz_scores": [],
        "reteach_triggered": False,
        "turn_count": 0,
    }

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        state["question"] = user_input
        state["student_answer"] = None

        try:
            state = run_tutor(state)
            answer = state.get("answer", "No response generated.")
            sources = state.get("sources", [])
            print(f"\nTutor: {answer}")
            if sources:
                print(f"       [Sources: {', '.join(sources)}]")
            print()
        except Exception as e:
            print(f"⚠️  Error: {e}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ai-tutor",
        description="AI Tutor Agent — LangChain + LangGraph + ChromaDB",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest
    p_ingest = sub.add_parser("ingest", help="Ingest documents into ChromaDB")
    p_ingest.add_argument("--file", type=str, help="Single file to ingest")
    p_ingest.add_argument("--path", type=str, default="./docs",
                          help="Directory to ingest (default: ./docs)")
    p_ingest.set_defaults(func=cmd_ingest)

    # stats
    p_stats = sub.add_parser("stats", help="Show knowledge base statistics")
    p_stats.set_defaults(func=cmd_stats)

    # chat
    p_chat = sub.add_parser("chat", help="Terminal chat REPL")
    p_chat.set_defaults(func=cmd_chat)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
