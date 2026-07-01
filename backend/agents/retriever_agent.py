from backend.agents.state import TutorState
from backend.nlp.tagger import tag_bloom_level
from backend.rag.reranker import rerank
from backend.rag.retriever import retrieve


def retriever_node(state: TutorState) -> TutorState:
    documents = retrieve(state["user_message"], state["session_id"])
    reranked = rerank(state["user_message"], documents)

    state["retrieved_chunks"] = [doc.page_content for doc in reranked]
    state["bloom_tags"] = [tag_bloom_level(doc.page_content) for doc in reranked]

    return state
