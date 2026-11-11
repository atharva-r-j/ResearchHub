-- ============================================================================
-- ResearchHub Sample Data
-- Step 3: Populate all 7 tables with realistic research papers, authors,
--         citations, users, bookmarks, and reading statuses.
-- ============================================================================

-- Clear existing data and reset auto-increment IDs back to 1
-- so our sample IDs (1, 2, 3...) match reliably every time.
TRUNCATE TABLE
    reading_status,
    bookmarks,
    citations,
    paper_authors,
    authors,
    papers,
    users
RESTART IDENTITY CASCADE;

-- ============================================================================
-- 1. USERS (3 sample users)
-- ============================================================================
INSERT INTO users (username, email, full_name) VALUES
('atharva_j',  'atharva@researchhub.edu',  'Atharva Jamakhandi'),
('tanisha',    'tanisha@researchhub.edu',     'Tanisha Reddy'),
('prof_mehta', 'mehta@researchhub.edu',    'Dr. Rajesh Mehta');

-- ============================================================================
-- 2. AUTHORS (12 researchers)
-- ============================================================================
INSERT INTO authors (name, affiliation) VALUES
('Ashish Vaswani',     'Google Brain'),
('Noam Shazeer',       'Google Brain'),
('Kaiming He',         'Microsoft Research'),
('Jian Sun',           'Microsoft Research'),
('Ian Goodfellow',     'University of Montreal'),
('Yoshua Bengio',      'University of Montreal'),
('Jacob Devlin',       'Google AI Language'),
('Rohan Kulkarni',     'IIT Bombay'),
('Ananya Deshmukh',    'DRDO Radar Systems Lab'),
('Vikram Nair',        'IISc Bangalore'),
('Yann LeCun',         'New York University'),
('Geoffrey Hinton',    'University of Toronto');

-- ============================================================================
-- 3. PAPERS (12 research papers across AI, ML, Radar, NLP, and Databases)
-- ============================================================================
INSERT INTO papers (title, abstract, publication_year, domain, pdf_path) VALUES
(
    'Attention Is All You Need',
    'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely for sequence transduction tasks.',
    2017,
    'Natural Language Processing',
    'data/papers/attention_is_all_you_need.pdf'
),
(
    'Deep Residual Learning for Image Recognition',
    'We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously, achieving state-of-the-art accuracy on ImageNet.',
    2016,
    'Computer Vision',
    'data/papers/resnet_deep_residual_learning.pdf'
),
(
    'Generative Adversarial Nets',
    'We propose a new framework for estimating generative models via an adversarial process in which we simultaneously train two models: a generative model G and a discriminative model D.',
    2014,
    'Deep Learning',
    'data/papers/generative_adversarial_nets.pdf'
),
(
    'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
    'We introduce BERT, designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.',
    2019,
    'Natural Language Processing',
    'data/papers/bert_pretraining.pdf'
),
(
    'Deep Autoencoder Networks for Radar Clutter Suppression and Signal Denoising',
    'This paper presents a convolutional denoising autoencoder architecture to remove Gaussian noise and ground clutter from FMCW radar echo signals in low-SNR environments.',
    2023,
    'Signal Processing',
    'data/papers/radar_autoencoder_denoising.pdf'
),
(
    'Residual Neural Filtering for Automotive Millimeter-Wave Radar Interference Mitigation',
    'We apply deep residual neural networks to clean corrupted radar spectrograms caused by mutual interference between nearby autonomous vehicle radar sensors.',
    2024,
    'Signal Processing',
    'data/papers/mmwave_radar_interference.pdf'
),
(
    'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
    'We explore a general-purpose fine-tuning recipe for retrieval-augmented generation models which combine pre-trained parametric memory with non-parametric vector index memory.',
    2020,
    'Natural Language Processing',
    'data/papers/rag_knowledge_nlp.pdf'
),
(
    'Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks',
    'We present a modification of the pretrained BERT network that uses siamese and triplet network structures to derive semantically meaningful sentence embeddings for fast similarity search.',
    2019,
    'Natural Language Processing',
    'data/papers/sentence_bert.pdf'
),
(
    'HNSW: Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs',
    'We propose a new approach for approximate K-nearest neighbor search based on navigable small world graphs with controllable hierarchy for high-dimensional vector databases.',
    2018,
    'Databases',
    'data/papers/hnsw_vector_search.pdf'
),
(
    'ImageNet Classification with Deep Convolutional Neural Networks',
    'We trained a large, deep convolutional neural network to classify 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into 1000 different classes.',
    2012,
    'Computer Vision',
    'data/papers/alexnet_imagenet.pdf'
),
(
    'Dropout: A Simple Way to Prevent Neural Networks from Overfitting',
    'Dropout is a technique for addressing overfitting in deep neural networks by randomly dropping units along with their connections during training.',
    2014,
    'Machine Learning',
    'data/papers/dropout_regularization.pdf'
),
(
    'Hybrid SQL and Vector Indexing for Academic Literature Discovery',
    'We study architectures that pair relational PostgreSQL metadata filtering with dense semantic vector retrieval to improve precision and recall in scientific search engines.',
    2025,
    'Databases',
    'data/papers/hybrid_sql_vector_search.pdf'
);

-- ============================================================================
-- 4. PAPER_AUTHORS (Connect papers to authors with author_order)
-- Notice how multiple papers share authors, and one paper can have multiple authors!
-- ============================================================================
INSERT INTO paper_authors (paper_id, author_id, author_order) VALUES
-- Paper 1: Attention Is All You Need -> Ashish Vaswani (1), Noam Shazeer (2)
(1, 1, 1),
(1, 2, 2),
-- Paper 2: ResNet -> Kaiming He (1), Jian Sun (2)
(2, 3, 1),
(2, 4, 2),
-- Paper 3: GANs -> Ian Goodfellow (1), Yoshua Bengio (2)
(3, 5, 1),
(3, 6, 2),
-- Paper 4: BERT -> Jacob Devlin (1), Ashish Vaswani (2)
(4, 7, 1),
(4, 1, 2),
-- Paper 5: Radar Denoising -> Ananya Deshmukh (1), Rohan Kulkarni (2)
(5, 9, 1),
(5, 8, 2),
-- Paper 6: mmWave Radar -> Rohan Kulkarni (1), Ananya Deshmukh (2), Vikram Nair (3)
(6, 8, 1),
(6, 9, 2),
(6, 10, 3),
-- Paper 7: RAG -> Jacob Devlin (1), Vikram Nair (2)
(7, 7, 1),
(7, 10, 2),
-- Paper 8: Sentence-BERT -> Jacob Devlin (1), Noam Shazeer (2)
(8, 7, 1),
(8, 2, 2),
-- Paper 9: HNSW -> Vikram Nair (1)
(9, 10, 1),
-- Paper 10: AlexNet -> Geoffrey Hinton (1), Yann LeCun (2)
(10, 12, 1),
(10, 11, 2),
-- Paper 11: Dropout -> Geoffrey Hinton (1)
(11, 12, 1),
-- Paper 12: Hybrid SQL & Vector -> Rohan Kulkarni (1), Vikram Nair (2)
(12, 8, 1),
(12, 10, 2);

-- ============================================================================
-- 5. CITATIONS (Which paper cites which paper)
-- citing_paper_id -> cited_paper_id
-- ============================================================================
INSERT INTO citations (citing_paper_id, cited_paper_id) VALUES
(2, 10),  -- ResNet cites AlexNet
(2, 11),  -- ResNet cites Dropout
(1, 11),  -- Attention cites Dropout
(4, 1),   -- BERT cites Attention Is All You Need
(5, 2),   -- Radar Denoising cites ResNet
(5, 3),   -- Radar Denoising cites GANs
(6, 2),   -- mmWave Radar cites ResNet
(6, 5),   -- mmWave Radar cites Radar Denoising
(7, 1),   -- RAG cites Attention Is All You Need
(7, 4),   -- RAG cites BERT
(8, 1),   -- Sentence-BERT cites Attention Is All You Need
(8, 4),   -- Sentence-BERT cites BERT
(12, 8),  -- Hybrid SQL & Vector cites Sentence-BERT
(12, 9);  -- Hybrid SQL & Vector cites HNSW

-- ============================================================================
-- 6. BOOKMARKS (Users saving papers for later)
-- ============================================================================
INSERT INTO bookmarks (user_id, paper_id) VALUES
(1, 1),
(1, 5),
(1, 12),
(2, 4),
(2, 8),
(3, 2);

-- ============================================================================
-- 7. READING_STATUS (Tracking reading progress)
-- Allowed statuses: 'want_to_read', 'reading', 'completed'
-- ============================================================================
INSERT INTO reading_status (user_id, paper_id, status) VALUES
(1, 1,  'completed'),
(1, 5,  'reading'),
(1, 12, 'want_to_read'),
(2, 4,  'completed'),
(2, 8,  'reading'),
(3, 2,  'completed');

