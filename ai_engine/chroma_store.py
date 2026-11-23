'''chroma_store.py
Persistent ChromaDB wrapper used by the AI module.
All IDs are stored as strings (the integer paper_id from PostgreSQL).
''' 

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb

# ----------------------------------------------------------------------
# Singleton client – created once per interpreter session.
# ChromaDB >= 1.0 uses PersistentClient instead of the old Settings API.
# ----------------------------------------------------------------------
_client: Optional[chromadb.PersistentClient] = None
_collection_name = "papers"


def _get_client() -> chromadb.PersistentClient:
    """Return a persistent Chroma client.

    The data directory lives at ``<repo_root>/data/chroma`` so that the vector
    store survives process restarts and is colocated with other project data.
    """
    global _client
    if _client is None:
        repo_root = Path(__file__).resolve().parents[1]
        persist_dir = repo_root / "data" / "chroma"
        os.makedirs(persist_dir, exist_ok=True)
        # PersistentClient is the modern API for ChromaDB >= 1.0
        _client = chromadb.PersistentClient(path=str(persist_dir))
    return _client


def _get_collection() -> chromadb.Collection:
    """Create (or fetch) the ``papers`` collection.

    We use cosine similarity (the default) – ``metadata`` can hold optional
    versioning information in the future.
    """
    client = _get_client()
    return client.get_or_create_collection(
        name=_collection_name,
        metadata={"hnsw:space": "cosine"},
    )

# ----------------------------------------------------------------------
# Public API used by ``semantic_search.py``
# ----------------------------------------------------------------------

def add(paper_id: int, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
    """Insert or update a paper embedding.

    Parameters
    ----------
    paper_id : int
        The integer primary key from PostgreSQL.
    embedding : List[float]
        Vector representation (typically length 384).
    metadata : dict, optional
        Additional metadata – not required for the prototype.
    """
    if not isinstance(paper_id, int):
        raise ValueError("paper_id must be an integer")
    if not embedding:
        raise ValueError("embedding must be a non‑empty vector")
    coll = _get_collection()
    coll.upsert(
        ids=[str(paper_id)],
        embeddings=[embedding],
        metadatas=[metadata or {}],
    )


def search(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Return the ``top_k`` most similar papers.

    The Chroma result provides *distance*; we convert it to a similarity score
    ``score = 1 - distance`` (range 0‑1, higher = more similar).
    """
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")
    coll = _get_collection()
    results = coll.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["distances"],   # ids are always returned automatically in chromadb >= 1.0
    )
    ids = results["ids"][0]
    distances = results["distances"][0]
    return [{"paper_id": int(pid), "score": round(1 - dist, 4)} for pid, dist in zip(ids, distances)]


def get_embedding(paper_id: int) -> List[float]:
    """Retrieve the stored embedding for a given paper_id.

    Returns the raw vector (list of floats). Raises ``KeyError`` if the ID is
    absent.
    """
    coll = _get_collection()
    result = coll.get(ids=[str(paper_id)], include=["embeddings"])
    embeddings = result.get("embeddings", [])
    if embeddings is None or len(embeddings) == 0:
        raise KeyError(f"Embedding for paper_id {paper_id} not found")
    return embeddings[0]


def delete(paper_id: int) -> None:
    """Remove a paper's embedding from the collection."""
    coll = _get_collection()
    coll.delete(ids=[str(paper_id)])
