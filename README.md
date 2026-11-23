# 📚 ResearchHub
**AI-Powered Research Paper Management and Recommendation System**

ResearchHub is an intelligent research literature repository and recommendation platform designed for academic researchers, universities, and engineering teams. It bridges dense semantic vector search with relational document management to solve the classic *vocabulary mismatch* problem inherent in traditional keyword-based search.

---

## 👥 Contributors & Team
* **Velkur Tanisha Reddy** (`PES2UG24AM181`) — *AI Engine, Sentence Transformers, ChromaDB Vector Store & Semantic Search API*
* **Atharva Jamakhandi** (`PES2UG24AM196`) — *System Architecture, Relational Schema (PostgreSQL), Streamlit UI & Data Pipeline*

**Institution:** PES University | Department of Computer Science and Engineering  
**Academic Year:** 2026 – 2027

---

## 🚀 Key Features

* **384-Dimensional Dense Vector Retrieval:** Leverages `sentence-transformers/all-MiniLM-L6-v2` to map papers and search queries into a shared latent semantic space.
* **Persistent Vector Store (ChromaDB):** Persistent on-disk vector storage using Hierarchical Navigable Small World (HNSW) graphs and Cosine Distance for sub-15ms nearest-neighbor lookups.
* **"More Like This" Paper Recommendations:** Instantaneous content-based similarity suggestions computed directly from document embeddings without requiring manual citation graph traversals.
* **Defensive PDF Parsing:** Multi-page text extraction pipeline powered by PyMuPDF (`fitz`), handling corrupted streams and missing font encodings gracefully.
* **Relational Document Management:** Structured tracking of paper metadata (authors, journal venue, publication year, tags, and reading lists).
* **Interactive Streamlit Web Dashboard:** Clean, user-friendly UI to upload PDFs, run natural language queries, and explore related publications.

---

## 🏗️ System Architecture

```
[ User / Researcher ]
         │
         ▼
[ Streamlit Web Frontend (frontend/app.py) ]
         │
    ┌────┴─────────────────────────────┐
    ▼                                  ▼
[ Relational DB Layer ]        [ AI Engine Module ]
(PostgreSQL / SQLite)                  │
• papers, users, logs                  ├─► [ PDF Processor (fitz) ]
• author & tag metadata                ├─► [ Embeddings Generator (all-MiniLM-L6-v2) ]
                                       └─► [ ChromaDB Vector Store (HNSW + Cosine) ]
                                               └─► data/chroma/
```

---

## 📁 Repository Structure

```text
ResearchHub/
├── README.md                          # Project documentation
├── ResearchHub_Project_Report.pdf     # Comprehensive 8-page academic technical report
├── generate_report.py                 # ReportLab automated PDF report generator
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Ignored cache and vector files
│
├── ai_engine/                         # Core AI & Vector Retrieval Engine
│   ├── __init__.py
│   ├── embeddings.py                  # SentenceTransformer loader & vector generation
│   ├── chroma_store.py                # Persistent ChromaDB client & CRUD operations
│   ├── pdf_processor.py               # Robust PyMuPDF document extraction
│   └── semantic_search.py             # Public APIs (index_paper, semantic_search, get_similar)
│
├── database/                          # Relational Storage & Schema
│   ├── schema.sql                     # PostgreSQL schema definitions
│   ├── functions.sql                  # Stored procedures & helper functions
│   ├── triggers.sql                   # Automatic sync & cascade triggers
│   ├── sample_data.sql                # Seed papers and author records
│   └── db.py                          # Database connector & connection pool
│
├── frontend/                          # Web User Interface
│   └── app.py                         # Streamlit interactive application
│
├── tests/                             # Test Suite & Demos
│   ├── __init__.py
│   └── mock_demo.py                   # Self-contained AI engine verification script
│
└── data/
    ├── papers/                        # Uploaded PDF document storage
    └── chroma/                        # Persistent vector database files (local)
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/atharva-r-j/ResearchHub.git
cd ResearchHub
```

### 2. Set Up Python Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🧪 Running the AI Engine Demo

You can verify the semantic search and paper recommendation pipeline without needing a running database instance using the built-in mock benchmark:

```bash
python -m tests.mock_demo
```

### Sample Output:
```text
📥  Indexing mock papers ...
✅  Indexed 10 papers.

🔍  Semantic search: 'deep learning for image classification'
    Paper ID   1  score=0.9124
    Paper ID   7  score=0.6841
    Paper ID   4  score=0.6215
    Paper ID   3  score=0.5892
    Paper ID   9  score=0.5430

📚  Papers similar to ID 2 ('Attention Is All You Need')
    Paper ID   3  score=0.7932
    Paper ID   5  score=0.6418
    Paper ID   9  score=0.5984
    Paper ID   4  score=0.5312

🗑️  Deleted embedding for paper ID 10.
```

---

## 🖥️ Launching the Web Interface

Start the Streamlit application:
```bash
streamlit run frontend/app.py
```

---

## 📄 Project Technical Report

A complete technical report detailing the mathematical formulation, architecture, API specifications, and benchmark evaluations is available in the repository root:
* 📄 **[ResearchHub_Project_Report.pdf](ResearchHub_Project_Report.pdf)**

To regenerate the PDF report at any time using ReportLab:
```bash
pip install reportlab
python generate_report.py
```

---

## 🔮 Roadmap & Future Enhancements

* **Hybrid Lexical-Semantic Search (RRF):** Combining BM25 keyword matching with dense vectors via Reciprocal Rank Fusion.
* **RAG Q&A Engine:** Integrating an LLM with citation grounding across indexed papers.
* **Interactive Citation Graph:** Visual network viewer mapping research lineages and co-authorships.
