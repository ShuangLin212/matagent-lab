from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from .models import Document, RetrievedDocument


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_+-]*")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOPWORDS]


def load_documents(path: str | Path) -> list[Document]:
    documents: list[Document] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            try:
                documents.append(Document(**payload))
            except TypeError as exc:
                raise ValueError(f"invalid document at {path}:{line_number}") from exc
    return documents


class ScientificRetrievalIndex:
    """Small BM25-style index for scientific notes and paper summaries."""

    def __init__(self, documents: list[Document]) -> None:
        if not documents:
            raise ValueError("retrieval index requires at least one document")
        self.documents = documents
        self.doc_tokens = [tokenize(document.text) for document in documents]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)
        self.term_frequencies = [Counter(tokens) for tokens in self.doc_tokens]
        self.doc_frequencies: Counter[str] = Counter()
        for tokens in self.doc_tokens:
            self.doc_frequencies.update(set(tokens))

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "ScientificRetrievalIndex":
        return cls(load_documents(path))

    def search(self, query: str, top_k: int = 4, domain: str | None = None) -> list[RetrievedDocument]:
        query_terms = tokenize(query)
        scored: list[tuple[float, int, list[str]]] = []
        allowed_domains = {domain, "general", "cross_domain", None}

        for index, document in enumerate(self.documents):
            if domain and document.domain not in allowed_domains:
                continue
            score, matched_terms = self._score_document(index, query_terms, document)
            if score > 0:
                scored.append((score, index, matched_terms))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedDocument(self.documents[index], round(score, 4), matched_terms)
            for score, index, matched_terms in scored[:top_k]
        ]

    def _score_document(
        self, document_index: int, query_terms: list[str], document: Document
    ) -> tuple[float, list[str]]:
        k1 = 1.4
        b = 0.75
        frequencies = self.term_frequencies[document_index]
        doc_length = self.doc_lengths[document_index]
        score = 0.0
        matched_terms: list[str] = []

        for term in query_terms:
            frequency = frequencies.get(term, 0)
            if frequency == 0:
                continue
            df = self.doc_frequencies[term]
            idf = math.log(1 + (len(self.documents) - df + 0.5) / (df + 0.5))
            denominator = frequency + k1 * (1 - b + b * doc_length / self.avg_doc_length)
            score += idf * (frequency * (k1 + 1)) / denominator
            matched_terms.append(term)

        tag_terms = {tag.lower() for tag in document.tags}
        material_terms = {material.lower() for material in document.materials}
        score += 0.25 * len(tag_terms.intersection(query_terms))
        score += 0.20 * len(material_terms.intersection(query_terms))
        return score, matched_terms

