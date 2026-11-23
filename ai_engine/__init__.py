# ai_engine/__init__.py
# Makes ai_engine a proper Python package so it can be imported from anywhere.
from .semantic_search import (
    index_paper,
    semantic_search,
    get_similar_papers,
    delete_paper_embedding,
)

__all__ = [
    "index_paper",
    "semantic_search",
    "get_similar_papers",
    "delete_paper_embedding",
]

