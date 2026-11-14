'''embeddings.py
Utility for loading a Sentence‑Transformers model and converting text into vector embeddings.
The module caches the loaded model so it is instantiated only once per interpreter session.
''' 

from __future__ import annotations

import logging
from typing import List, Optional

from sentence_transformers import SentenceTransformer
import numpy as np

# Configure a very small logger – useful during debugging but silent by default.
_logger = logging.getLogger(__name__)
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[embeddings] %(levelname)s: %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Model loading – a singleton pattern. The heavy model is loaded the first time
# `load_model()` is called. Subsequent calls simply return the cached instance.
# ---------------------------------------------------------------------------
_model: Optional[SentenceTransformer] = None


def load_model() -> SentenceTransformer:
    """Load (or retrieve) the Sentence‑Transformer model.

    The default model, ``all‑MiniLM‑L6‑v2``, is small (≈ 20 MB) and provides a
    384‑dimensional embedding suitable for semantic search.  It is downloaded
    automatically on the first run and cached by the ``sentence_transformers``
    library.

    Returns
    -------
    SentenceTransformer
        The ready‑to‑use model instance.
    """
    global _model
    if _model is None:
        _logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'…")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _logger.info("Model loaded.")
    return _model


def embed_text(title: str | None, abstract: str | None) -> List[float]:
    """Generate a single embedding from a paper *title* and *abstract*.

    Parameters
    ----------
    title: str | None
        The research paper title. ``None`` or empty string is treated as missing.
    abstract: str | None
        The abstract text. ``None`` or empty string is treated as missing.

    Returns
    -------
    List[float]
        384‑dimensional vector (list of floats) ready for ChromaDB.

    Raises
    ------
    ValueError
        If **both** ``title`` and ``abstract`` are missing/empty.
    """
    # Normalise inputs – guard against ``None``.
    title_clean = (title or "").strip()
    abstract_clean = (abstract or "").strip()

    if not title_clean and not abstract_clean:
        raise ValueError("At least one of title or abstract must be non‑empty for embedding generation.")

    # Concatenate with a simple separator; the transformer treats it as a single sentence.
    text = f"{title_clean}\n{abstract_clean}" if title_clean and abstract_clean else title_clean or abstract_clean

    model = load_model()
    # ``model.encode`` returns a numpy array (shape (1, dim)).
    embedding: np.ndarray = model.encode([text], normalize_embeddings=True)[0]
    # Convert to plain Python list for JSON‑serialisable storage.
    return embedding.tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Generate normalized embeddings for a batch of text strings.

    Parameters
    ----------
    texts : List[str]
        List of texts (e.g., concatenated title and abstract).

    Returns
    -------
    List[List[float]]
        List of 384-dimensional vector embeddings.
    """
    if not texts:
        return []

    model = load_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]


