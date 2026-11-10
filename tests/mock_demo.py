'''mock_demo.py
Simple script to demonstrate the AI module without needing PostgreSQL.
It creates ten mock papers, indexes them, runs a semantic search and a
"similar papers" query, then prints the results.
''' 

from pathlib import Path
import random

# Ensure the data directory exists (Chroma will create its own sub‑dir).
# Import the public API.
from ai_engine.semantic_search import index_paper, semantic_search, get_similar_papers, delete_paper_embedding

# ----------------------------------------------------------------------
# Mock paper generator – titles and abstracts are fabricated but varied.
# ----------------------------------------------------------------------

def generate_mock_papers(num: int = 10):
    topics = [
        "machine learning",
        "computer vision",
        "natural language processing",
        "graph neural networks",
        "reinforcement learning",
        "quantum computing",
        "bioinformatics",
        "software engineering",
        "data mining",
        "information retrieval",
    ]
    papers = []
    for i in range(1, num + 1):
        topic = random.choice(topics)
        title = f"Advances in {topic.title()} {i}"
        abstract = (
            f"This paper discusses recent developments in {topic}. "
            f"We present experiments, results, and future directions for {topic}."
        )
        papers.append({"paper_id": i, "title": title, "abstract": abstract})
    return papers


def main():
    # 1️⃣ Index mock papers
    papers = generate_mock_papers()
    for p in papers:
        index_paper(p["paper_id"], p["title"], p["abstract"])
    print("✅ Indexed", len(papers), "mock papers.")

    # 2️⃣ Semantic search demo
    query = "deep learning for image classification"
    results = semantic_search(query, top_k=5)
    print("\n🔍 Semantic search results for query:", query)
    for r in results:
        print(f"  Paper ID {r['paper_id']}: score {r['score']}")

    # 3️⃣ Similar‑paper demo (pick a random paper)
    ref_id = random.choice(papers)["paper_id"]
    similar = get_similar_papers(ref_id, top_k=5)
    print(f"\n📚 Papers similar to ID {ref_id}:")
    for r in similar:
        print(f"  Paper ID {r['paper_id']}: score {r['score']}")

    # 4️⃣ Cleanup example – delete one embedding
    delete_paper_embedding(ref_id)
    print(f"\n🗑️ Deleted embedding for paper ID {ref_id}.")

if __name__ == "__main__":
    main()

