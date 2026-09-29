from pathlib import Path

from app.rag.retriever import KnowledgeRetriever


def test_retriever_has_documents():
    retriever = KnowledgeRetriever(Path("app/rag/documents"))
    assert len(retriever.documents) >= 4
