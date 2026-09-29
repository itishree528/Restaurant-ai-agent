from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeRetriever:
    """Small local TF-IDF retrieval layer for the assessment knowledge base."""

    def __init__(self, documents_dir: Path):
        self.documents_dir = documents_dir
        self.documents: list[dict] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self._load()

    def _load(self) -> None:
        self.documents.clear()

        for path in sorted(self.documents_dir.glob("*.txt")):
            text = path.read_text(encoding="utf-8").strip()
            if text:
                self.documents.append(
                    {"source": path.name, "content": text}
                )

        if self.documents:
            self.matrix = self.vectorizer.fit_transform(
                [doc["content"] for doc in self.documents]
            )

    def search(self, query: str, top_k: int = 3, threshold: float = 0.10) -> list[dict]:
        if not self.documents or self.matrix is None:
            return []

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]

        ranked = sorted(
            zip(scores, self.documents),
            key=lambda item: item[0],
            reverse=True,
        )

        results = []
        for score, document in ranked[:top_k]:
            if float(score) >= threshold:
                results.append(
                    {
                        "source": document["source"],
                        "content": document["content"],
                        "score": round(float(score), 4),
                    }
                )

        return results
