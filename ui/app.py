"""
ui/app.py
─────────
Streamlit chat interface for the AI Tutor Agent.

Layout:
  ┌─────────────────────────────────────────────────────────┐
  │  Sidebar                    │   Main chat area          │
  │  ─────────                  │   ─────────────           │
  │  📤 Document uploader       │   💬 Conversation history │
  │  📊 Session stats           │   📝 Chat input           │
  │  📥 Export report button    │                           │
  └─────────────────────────────────────────────────────────┘

Session state keys used:
  messages        — list of {role, content} dicts
  tutor_state     — TutorState dict persisted across turns
  kb_stats        — knowledge base counts
  session_start   — ISO timestamp
"""

from __future__ import annotations

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from loguru import logger

from config.settings import get_settings
from agents.graph import run_tutor
from agents.state import TutorState
from ingest.pipeline import ingest_uploaded_bytes, get_kb_stats
from ui.exporter import generate_session_report

# ─────────────────────────────────────────────────────────────────────────────
cfg = get_settings()

st.set_page_config(
    page_title="AI Tutor Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    .chat-msg-user   { background:#1e3a5f; border-radius:12px; padding:10px 14px; margin:4px 0; }
    .chat-msg-tutor  { background:#1a2634; border-radius:12px; padding:10px 14px; margin:4px 0; }
    .stat-card { background:#1a2634; border-radius:8px; padding:8px 12px; margin:4px 0; font-size:13px; }
    .weak-pill { background:#7f1d1d; color:#fca5a5; border-radius:20px;
                 padding:2px 10px; font-size:11px; margin:2px; display:inline-block; }
    .topic-pill { background:#1e3a5f; color:#93c5fd; border-radius:20px;
                  padding:2px 10px; font-size:11px; margin:2px; display:inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session state initialisation ─────────────────────────────────────────────
def _init_session() -> None:
    defaults: Dict[str, Any] = {
        "messages": [],
        "tutor_state": TutorState(
            session_topics=[],
            weak_topics=[],
            quiz_scores=[],
            reteach_triggered=False,
            turn_count=0,
        ),
        "kb_stats": get_kb_stats(),
        "session_start": datetime.now().isoformat()[:19],
        "student_name": "Student",
        "last_quiz": None,
        "awaiting_answer": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_session()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 AI Tutor")
    st.caption("Powered by LangChain · LangGraph · ChromaDB")
    st.divider()

    # Student name
    st.session_state.student_name = st.text_input(
        "Your name", value=st.session_state.student_name
    )

    st.subheader("📤 Upload Study Material")
    uploaded_files = st.file_uploader(
        "PDF · DOCX · TXT",
        type=["pdf", "docx", "doc", "txt", "md"],
        accept_multiple_files=True,
        key="file_uploader",
    )

    if uploaded_files:
        with st.spinner("Ingesting documents…"):
            results = []
            for uf in uploaded_files:
                try:
                    r = ingest_uploaded_bytes(uf.read(), uf.name)
                    results.append(r)
                except Exception as e:
                    st.error(f"Failed to ingest {uf.name}: {e}")
            if results:
                for r in results:
                    st.success(
                        f"✅ **{r['source']}** — "
                        f"{r['chunks_ingested']} new chunks ingested"
                    )
                # Refresh stats
                st.session_state.kb_stats = get_kb_stats()

    st.divider()
    st.subheader("📚 Knowledge Base")
    kb = st.session_state.kb_stats
    st.markdown(
        f"""
        <div class="stat-card">
        📄 <b>{kb.get('total_chunks', 0)}</b> chunks indexed<br>
        🗂 <b>{len(kb.get('unique_sources', []))}</b> documents
        </div>
        """,
        unsafe_allow_html=True,
    )
    if kb.get("unique_sources"):
        with st.expander("Indexed documents"):
            for src in kb["unique_sources"]:
                st.text(f"• {src}")

    st.divider()
    st.subheader("📊 Session Stats")
    ts = st.session_state.tutor_state
    topics = ts.get("session_topics", [])
    weak = ts.get("weak_topics", [])
    scores = ts.get("quiz_scores", [])
    turns = ts.get("turn_count", 0)

    st.markdown(f"<div class='stat-card'>💬 Turns: <b>{turns}</b></div>", unsafe_allow_html=True)

    if topics:
        pills = " ".join(f"<span class='topic-pill'>{t}</span>" for t in topics[-8:])
        st.markdown(f"**Topics covered:**<br>{pills}", unsafe_allow_html=True)

    if weak:
        pills = " ".join(f"<span class='weak-pill'>⚠ {w}</span>" for w in weak)
        st.markdown(f"**Weak areas:**<br>{pills}", unsafe_allow_html=True)

    if scores:
        avg = sum(scores) / len(scores)
        st.markdown(
            f"<div class='stat-card'>📝 Quizzes: <b>{len(scores)}</b> | "
            f"Avg: <b>{avg:.1f}</b></div>",
            unsafe_allow_html=True,
        )
        # Mini score bar chart
        st.bar_chart({"score": scores}, height=80)

    st.divider()
    st.subheader("📥 Export Report")
    if st.button("Download PDF Report", use_container_width=True):
        session_data = {
            "student_name": st.session_state.student_name,
            "session_start": st.session_state.session_start,
            "topics_covered": topics,
            "weak_topics": weak,
            "quiz_scores": scores,
            "qa_history": [],
        }
        pdf_bytes = generate_session_report(session_data)
        st.download_button(
            label="💾 Save PDF",
            data=pdf_bytes,
            file_name=f"tutor_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ── Main chat area ────────────────────────────────────────────────────────────
st.title("💬 AI Tutor Chat")
st.caption(
    "I'm Socrates, your AI tutor. Ask me anything about your uploaded materials, "
    "request a quiz, or ask me to explain a concept."
)

# Render conversation history
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role, avatar="🧑‍🎓" if role == "user" else "🏛"):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
placeholder = (
    "Type your answer…"
    if st.session_state.awaiting_answer
    else "Ask a question, request a quiz, or say 'explain [topic]'…"
)

if user_input := st.chat_input(placeholder):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_input)

    # Build state for this turn
    current_state: TutorState = dict(st.session_state.tutor_state)  # type: ignore

    # Detect if this is an answer to an active quiz
    is_answering_quiz = (
        st.session_state.awaiting_answer
        and st.session_state.last_quiz is not None
    )

    if is_answering_quiz:
        current_state["question"] = f"Evaluate: {user_input}"
        current_state["student_answer"] = user_input
        current_state["quiz"] = st.session_state.last_quiz
        # Force evaluator routing
        current_state["next_action"] = "evaluator"
        # Temporarily override intent so planner knows
        current_state["intent"] = "Evaluate"
    else:
        current_state["question"] = user_input
        current_state["student_answer"] = None

    # Run graph
    with st.chat_message("assistant", avatar="🏛"):
        with st.spinner("Thinking…"):
            try:
                updated_state = run_tutor(current_state)
                answer = updated_state.get("answer", "I'm sorry, I couldn't generate a response.")
                sources = updated_state.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("📎 Sources"):
                        for s in sources:
                            st.caption(f"• {s}")

                # Update persistent state
                st.session_state.tutor_state = updated_state
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

                # Track active quiz
                new_quiz = updated_state.get("quiz")
                if new_quiz and new_quiz.get("type") != "error":
                    st.session_state.last_quiz = new_quiz
                    st.session_state.awaiting_answer = True
                elif is_answering_quiz:
                    st.session_state.awaiting_answer = False
                    st.session_state.last_quiz = None

                # Reteach notification
                if updated_state.get("reteach_triggered") and is_answering_quiz:
                    st.info(
                        "🔄 You scored below 60% on that topic. "
                        "I'll re-explain it — just ask me to continue."
                    )

            except Exception as e:
                error_msg = f"⚠️ An error occurred: {e}"
                st.error(error_msg)
                logger.exception("Graph execution error")
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
