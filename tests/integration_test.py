"""Quick integration test: indexes all papers into ChromaDB then runs semantic search."""
import sys
sys.path.insert(0, '.')

from database.db import get_all_papers, get_papers_by_ids
from ai_engine.semantic_search import index_paper, semantic_search, get_similar_papers

# Step 1: Index all papers from PostgreSQL into ChromaDB
papers = get_all_papers()
print(f"Indexing {len(papers)} papers into ChromaDB...")
for p in papers:
    index_paper(p["paper_id"], p["title"], p["abstract"] or "")
print(f"Indexed {len(papers)} papers. OK!")

# Step 2: Semantic search
query = "radar signal denoising deep learning"
results = semantic_search(query, top_k=3)
print(f"\nSemantic search for: '{query}'")
for r in results:
    print(f"  paper_id={r['paper_id']}  score={r['score']}")

# Step 3: get_papers_by_ids bridge (AI -> PostgreSQL)
paper_ids = [r["paper_id"] for r in results]
full_papers = get_papers_by_ids(paper_ids)
print("\nFull metadata from PostgreSQL (in ranked order):")
for p in full_papers:
    print(f"  [{p['paper_id']}] {p['title']} ({p['domain']})")

# Step 4: Similar papers recommendation
ref_id = full_papers[0]["paper_id"]
similar = get_similar_papers(ref_id, top_k=2)
similar_papers = get_papers_by_ids([s["paper_id"] for s in similar])
print(f"\nPapers similar to paper {ref_id}:")
for p in similar_papers:
    print(f"  [{p['paper_id']}] {p['title']}")

print("\nALL INTEGRATION CHECKS PASSED!")

