"""
Test suite for ResearchHub AI Engine
Covers: embeddings, chroma_store, semantic_search, and pdf_processor.
"""

import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.embeddings import embed_text, embed_batch
from ai_engine.chroma_store import add, add_batch, search, get_embedding, delete
from ai_engine.semantic_search import (
    index_paper,
    index_papers_batch,
    semantic_search,
    get_similar_papers,
    delete_paper_embedding,
)
from ai_engine.pdf_processor import extract_text_from_pdf


class TestEmbeddings(unittest.TestCase):
    def test_embed_text_dimensions(self):
        emb = embed_text("Machine Learning", "An introduction to neural networks.")
        self.assertIsInstance(emb, list)
        self.assertEqual(len(emb), 384)
        self.assertIsInstance(emb[0], float)

    def test_embed_text_title_only(self):
        emb = embed_text("Quantum Computing", None)
        self.assertEqual(len(emb), 384)

    def test_embed_text_empty_raises(self):
        with self.assertRaises(ValueError):
            embed_text("", "   ")

    def test_embed_batch(self):
        texts = ["Natural language processing", "Computer vision with CNNs"]
        embeddings = embed_batch(texts)
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0]), 384)
        self.assertEqual(len(embeddings[1]), 384)


class TestChromaStore(unittest.TestCase):
    def setUp(self):
        self.test_id_1 = 90001
        self.test_id_2 = 90002

    def tearDown(self):
        for pid in [self.test_id_1, self.test_id_2]:
            try:
                delete(pid)
            except Exception:
                pass

    def test_add_get_and_delete(self):
        emb = embed_text("Robotics and Automation", "Path planning algorithms.")
        add(self.test_id_1, emb, {"title": "Robotics and Automation"})
        retrieved_emb = get_embedding(self.test_id_1)
        self.assertEqual(len(retrieved_emb), 384)

        delete(self.test_id_1)
        with self.assertRaises(KeyError):
            get_embedding(self.test_id_1)

    def test_search(self):
        emb1 = embed_text("Reinforcement Learning", "Q-learning and policy gradients.")
        emb2 = embed_text("Relational Databases", "B-tree indexing and query optimization.")
        add_batch(
            [self.test_id_1, self.test_id_2],
            [emb1, emb2],
            [{"title": "RL Paper"}, {"title": "DBMS Paper"}],
        )

        query_emb = embed_text("Deep Q-learning agents", "")
        results = search(query_emb, top_k=2)
        self.assertTrue(len(results) >= 1)
        # The RL paper should rank highest
        top_result_id = results[0]["paper_id"]
        self.assertEqual(top_result_id, self.test_id_1)


class TestSemanticSearch(unittest.TestCase):
    def setUp(self):
        self.p1 = 90101
        self.p2 = 90102
        index_paper(self.p1, "Convolutional Networks for Vision", "Object detection with ResNet.")
        index_paper(self.p2, "Graph Neural Networks", "Node classification and link prediction.")

    def tearDown(self):
        for pid in [self.p1, self.p2]:
            try:
                delete_paper_embedding(pid)
            except Exception:
                pass

    def test_semantic_search_ranking(self):
        results = semantic_search("Image recognition and ConvNets", top_k=2)
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["paper_id"], self.p1)
        self.assertGreater(results[0]["score"], 0.4)

    def test_get_similar_papers(self):
        # Index another vision paper
        p3 = 90103
        try:
            index_paper(p3, "Vision Transformers for Image Classification", "ViT applied to computer vision.")
            similar = get_similar_papers(self.p1, top_k=5)
            sim_ids = [s["paper_id"] for s in similar]
            self.assertIn(p3, sim_ids)
            self.assertNotIn(self.p1, sim_ids)  # Must exclude self
        finally:
            delete_paper_embedding(p3)

    def test_index_papers_batch(self):
        batch = [
            {"paper_id": 90201, "title": "Batch Paper 1", "abstract": "Cloud infrastructure."},
            {"paper_id": 90202, "title": "Batch Paper 2", "abstract": "Distributed systems."},
        ]
        count = index_papers_batch(batch)
        self.assertEqual(count, 2)
        for p in batch:
            delete_paper_embedding(p["paper_id"])


class TestPdfProcessor(unittest.TestCase):
    def test_nonexistent_pdf(self):
        text = extract_text_from_pdf("nonexistent_file_path.pdf")
        self.assertEqual(text, "")

    def test_extract_from_synthetic_pdf(self):
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "ResearchHub Test Document Text")
        pdf_bytes = doc.tobytes()
        doc.close()

        extracted = extract_text_from_pdf(pdf_bytes)
        self.assertIn("ResearchHub Test Document Text", extracted)


if __name__ == "__main__":
    unittest.main()
