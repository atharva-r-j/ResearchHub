'''semantic_search.py
High‑level API exposing the required functions for the ResearchHub AI module.
It ties together ``embeddings.py``, ``chroma_store.py`` and provides a thin
wrapper that respects the specification.
''' 

from __future__ import annotations

from typing import List, Dict, Any

from .embeddings import embed_text, embed_batch
from .chroma_store import (
    add as _cs_add,
    add_batch as _cs_add_batch,
    search as _cs_search,
    delete as _cs_delete,
    get_embedding as _cs_get_embedding,
)

# ----------------------------------------------------------------------
# Public functions required by the project specification
# ----------------------------------------------------------------------

def index_paper(paper_id: int, title: str, abstract: str) -> None:
    """Generate an embedding for ``title`` + ``abstract`` and store it.

    Parameters
    ----------
    paper_id : int
        Primary key coming from PostgreSQL.
    title : str
        Paper title.
    abstract : str
        Paper abstract.
    """
    if not isinstance(paper_id, int):
        raise ValueError("paper_id must be an integer")
    embedding = embed_text(title, abstract)
    _cs_add(paper_id, embedding, metadata={"title": title, "abstract": abstract})


def index_papers_batch(papers: List[Dict[str, Any]]) -> int:
    """Batch-index multiple papers into ChromaDB in a vectorized operation.

    Parameters
    ----------
    papers : List[Dict[str, Any]]
        List of paper dicts containing at least 'paper_id' and 'title'.

    Returns
    -------
    int
        Count of successfully indexed papers.
    """
    valid_papers = []
    texts = []
    for p in papers:
        pid = p.get("paper_id")
        title = (p.get("title") or "").strip()
        abstract = (p.get("abstract") or "").strip()
        if pid is not None and (title or abstract):
            valid_papers.append(p)
            text = f"{title}\n{abstract}" if title and abstract else (title or abstract)
            texts.append(text)

    if not valid_papers:
        return 0

    embeddings = embed_batch(texts)
    ids = [p["paper_id"] for p in valid_papers]
    metadatas = [{"title": p.get("title", ""), "abstract": p.get("abstract", "") or ""} for p in valid_papers]

    _cs_add_batch(ids, embeddings, metadatas=metadatas)
    return len(valid_papers)


def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Return the most relevant paper IDs for a free‑text search query.

    The query is embedded with the same model used for indexing.
    The function returns a list of ``{"paper_id": int, "score": float}``.
    """
    if not query:
        raise ValueError("query must be a non‑empty string")
    query_emb = embed_text(query, "")
    return _cs_search(query_emb, top_k)


def get_similar_papers(paper_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
    """Find *top_k* papers most similar to the given ``paper_id``.

    This implements a classic *"more like this"* use‑case.
    """
    if not isinstance(paper_id, int):
        raise ValueError("paper_id must be an integer")
    try:
        embedding = _cs_get_embedding(paper_id)
    except KeyError as exc:
        raise ValueError(str(exc))
    results = _cs_search(embedding, top_k + 1)  # include possibly the paper itself
    # Remove self‑match if present
    filtered = [r for r in results if r["paper_id"] != paper_id]
    return filtered[:top_k]


def delete_paper_embedding(paper_id: int) -> None:
    """Delete the vector embedding for ``paper_id`` from ChromaDB."""
    if not isinstance(paper_id, int):
        raise ValueError("paper_id must be an integer")
    _cs_delete(paper_id)

