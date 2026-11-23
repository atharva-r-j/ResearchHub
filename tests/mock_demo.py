'''mock_demo.py – run with: python -m tests.mock_demo (from repo root)'''
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
from ai_engine.semantic_search import (
    index_paper, semantic_search, get_similar_papers, delete_paper_embedding
)

MOCK_PAPERS = [
    (1,  "Deep Learning for Image Classification",
         "We study convolutional neural networks for large-scale image recognition tasks."),
    (2,  "Attention Is All You Need",
         "We propose a Transformer model based solely on attention mechanisms for NLP."),
    (3,  "BERT: Pre-training of Deep Bidirectional Transformers",
         "BERT obtains state-of-the-art results on eleven natural language processing tasks."),
    (4,  "Graph Neural Networks: A Review",
         "We survey GNN methods and their applications to molecular biology and social networks."),
    (5,  "Reinforcement Learning with Human Feedback",
         "Fine-tuning large language models with RLHF produces safer AI assistants."),
    (6,  "Quantum Computing for Machine Learning",
         "We explore quantum algorithms that offer exponential speed-up for ML workloads."),
    (7,  "Variational Autoencoders for Generative Modeling",
         "VAEs learn latent representations and generate high-quality images and text."),
    (8,  "Data Mining Techniques for Big Data",
         "We review scalable association rule mining, clustering, and anomaly detection."),
    (9,  "Information Retrieval with Dense Vectors",
         "Dense retrieval outperforms BM25 on open-domain question answering benchmarks."),
    (10, "Bioinformatics and Protein Structure Prediction",
         "AlphaFold predicts protein 3D structures with near-experimental accuracy."),
]

def main():
    print("\n📥  Indexing mock papers ...")
    for pid, title, abstract in MOCK_PAPERS:
        index_paper(pid, title, abstract)
    print(f"✅  Indexed {len(MOCK_PAPERS)} papers.\n")

    query = "deep learning for image classification"
    print(f"🔍  Semantic search: '{query}'")
    for r in semantic_search(query, top_k=5):
        print(f"    Paper ID {r['paper_id']:>3}  score={r['score']:.4f}")

    ref_id = 2
    print(f"\n📚  Papers similar to ID {ref_id} ('{MOCK_PAPERS[ref_id-1][1]}')")
    for r in get_similar_papers(ref_id, top_k=5):
        print(f"    Paper ID {r['paper_id']:>3}  score={r['score']:.4f}")

    victim = 10
    delete_paper_embedding(victim)
    print(f"\n🗑️  Deleted embedding for paper ID {victim}.\n")

if __name__ == "__main__":
    main()
