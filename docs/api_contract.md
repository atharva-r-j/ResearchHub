# ResearchHub API Contract

> **Purpose:** This document tells your teammate (AI module developer) exactly which
> Python functions she can call from the `database/` module and what they return.
> She should **never** write SQL or connect to PostgreSQL directly.

---

## Setup

```python
from database.db import (
    add_paper,
    get_paper,
    get_papers_by_ids,
    search_papers,
    add_citation,
)
```

---

## 1. `add_paper(paper_data) -> int`

Inserts a new paper and its authors into PostgreSQL. Returns the new `paper_id`.

**Input:**

```python
paper_data = {
    "title": "Example Research Paper",           # REQUIRED (str)
    "abstract": "This paper explores...",         # optional (str)
    "publication_year": 2024,                     # optional (int, 1900-2100)
    "domain": "Machine Learning",                 # optional (str)
    "pdf_path": "data/papers/example.pdf",        # optional (str)
    "authors": ["Author One", "Author Two"],      # optional (list of str or dict)
}
```

**Output:** `int` — the `paper_id` to use when storing embeddings in ChromaDB.

**Example:**

```python
paper_id = add_paper({
    "title": "Radar Signal Denoising with Autoencoders",
    "abstract": "We propose a convolutional denoising autoencoder...",
    "publication_year": 2023,
    "domain": "Signal Processing",
    "pdf_path": "data/papers/radar_denoising.pdf",
    "authors": ["Ananya Deshmukh", "Rohan Kulkarni"],
})
# paper_id = 13  (use this ID when storing the embedding in ChromaDB)
```

---

## 2. `get_paper(paper_id) -> dict | None`

Retrieves a single paper's metadata including its authors.

**Input:** `int` — paper_id

**Output:**

```python
{
    "paper_id": 5,
    "title": "Deep Autoencoder Networks for Radar Clutter Suppression...",
    "abstract": "This paper presents a convolutional denoising...",
    "publication_year": 2023,
    "domain": "Signal Processing",
    "pdf_path": "data/papers/radar_autoencoder_denoising.pdf",
    "citation_count": 1,
    "authors": ["Ananya Deshmukh", "Rohan Kulkarni"],
}
```

Returns `None` if the paper_id does not exist.

---

## 3. `get_papers_by_ids(paper_ids) -> list[dict]`

> **This is the main integration function.**
>
> ChromaDB semantic search returns a ranked list of `paper_id`s.
> Pass them here to get full metadata from PostgreSQL.
> **The output order matches the input order** (preserving similarity ranking).

**Input:** `list[int]` — paper_ids in ranked order from ChromaDB

**Output:** `list[dict]` — same format as `get_paper()`, in the same order

**Example:**

```python
# ChromaDB returns these IDs ranked by semantic similarity
chroma_results = [6, 5, 1]

# Get full metadata while preserving the ranking
papers = get_papers_by_ids(chroma_results)
# papers[0]["title"] = "Residual Neural Filtering for Automotive..."  (most similar)
# papers[1]["title"] = "Deep Autoencoder Networks for Radar..."
# papers[2]["title"] = "Attention Is All You Need"                     (least similar)
```

---

## 4. `search_papers(filters) -> list[dict]`

Keyword-based search across PostgreSQL. All filters are optional and combinable.

**Input:**

```python
filters = {
    "title": "radar",                   # partial match, case-insensitive
    "author": "Rohan",                  # partial match on author name
    "publication_year": 2023,           # exact year (also accepts key "year")
    "domain": "Signal Processing",      # partial match
    "keyword": "denoising",             # searches in title AND abstract
}
```

**Output:** `list[dict]` — matching papers sorted by citation_count (descending)

---

## 5. `add_citation(citing_id, cited_id) -> bool`

Records that one paper cites another. Returns `True` if added, `False` if blocked
(self-citation, duplicate, or invalid IDs).

```python
success = add_citation(citing_id=5, cited_id=2)
# True  -> Paper 5 now cites Paper 2
# False -> blocked (self-cite, duplicate, or bad ID)
```

---

## Shared Key: `paper_id`

The `paper_id` (integer) is the **shared identifier** between PostgreSQL and ChromaDB.

```
PostgreSQL:  papers.paper_id = 5
ChromaDB:    document id = "5"  (store as string, convert with int())
```

When storing embeddings in ChromaDB, use `str(paper_id)` as the document ID.
When retrieving results from ChromaDB, convert back with `int(doc_id)` before
calling `get_papers_by_ids()`.
