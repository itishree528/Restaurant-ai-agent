from pathlib import Path

from app.rag.retriever import KnowledgeRetriever


def test_cancellation_retrieval():
    documents_dir = Path("app/rag/documents")
    retriever = KnowledgeRetriever(documents_dir)

    results = retriever.search("Can I cancel my order after restaurant acceptance?")

    assert results
    assert any("cancellation.txt" in item["source"] for item in results)
