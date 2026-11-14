# 📚 ResearchHub

> **AI-Powered Research Paper Management, Discovery & Recommendation System**  
> *DBMS 5th Semester Mini Project*

ResearchHub combines a robust **PostgreSQL** relational database with a persistent **ChromaDB** vector store and a **Streamlit** web application to provide unified research paper management, citation network tracking, and semantic search.

---

## 🌟 Key Features

* **Dual-Mode Discovery:**
  * **Keyword Search:** Filter by title, author name, domain, publication year, and abstract keywords directly via SQL.
  * **Semantic Search (AI):** Search papers using free-form conceptual queries powered by Sentence Transformers (`all-MiniLM-L6-v2`) and ChromaDB vector search.
* **Paper Ingestion & PDF Parsing:** Upload PDF research papers with automatic textual extraction using PyMuPDF (`fitz`), auto-populating metadata and synchronizing vector embeddings.
* **Citation Tracking & Auto-Triggers:**
  * Self-referencing citation relationships between papers.
  * PostgreSQL triggers that automatically maintain and synchronize citation counts upon citation creation or deletion.
  * Multi-directional citation exploration (citing papers vs. referenced papers).
* **"More Like This" Recommendations:** Vector-similarity recommendations for any paper in the repository.
* **User Reading List & Bookmarks:** Personalized bookmarking and reading status tracking (`want_to_read`, `reading`, `completed`).
* **Interactive Dashboard:** Aggregated analytics, domain distribution charts, and top-cited paper leaderboards powered by PostgreSQL views and stored functions.

---

## 🏗️ Architecture

```
ResearchHub/
├── ai_engine/               # AI vector search & embedding module
│   ├── chroma_store.py      # ChromaDB persistent vector database client
│   ├── embeddings.py        # Sentence-Transformers embedding generator
│   ├── pdf_processor.py     # PyMuPDF text extractor from PDF uploads
│   └── semantic_search.py   # High-level semantic search & recommender API
├── database/                # Relational database module (PostgreSQL)
│   ├── db.py                # Database connector & CRUD operations
│   ├── schema.sql           # Tables, constraints, and indexes
│   ├── sample_data.sql      # Seed papers, authors, citations, and users
│   ├── triggers.sql         # Citation count & timestamp triggers
│   └── functions.sql        # Views and stored procedures for analytics
├── frontend/                # Streamlit presentation layer
│   └── app.py               # Multi-page interactive web UI
├── docs/                    # Project documentation
│   ├── architecture.md      # Detailed system architecture & design
│   └── api_contract.md      # Integration contract between DB and AI engine
├── tests/                   # Verification & test suites
│   ├── test_database.py     # 69 database unit & integration tests
│   ├── test_ai_engine.py    # 11 AI engine unit tests
│   ├── integration_test.py  # End-to-end DB + AI integration test
│   └── mock_demo.py         # Standalone mock demo script
├── data/
│   ├── chroma/              # Persistent vector embeddings (ignored in git)
│   └── papers/              # Uploaded PDF files
├── .env                     # PostgreSQL connection credentials
├── requirements.txt         # Project dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.10+** (Tested on Python 3.11)
* **PostgreSQL 14+** (Tested on PostgreSQL 18.x)

### 2. Environment Configuration
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=researchhub
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Execute the SQL scripts in PostgreSQL in the following order:
```bash
psql -U postgres -d researchhub -f database/schema.sql
psql -U postgres -d researchhub -f database/triggers.sql
psql -U postgres -d researchhub -f database/functions.sql
psql -U postgres -d researchhub -f database/sample_data.sql
```

### 5. Run the Application
Start the Streamlit web interface:
```bash
streamlit run frontend/app.py
```

---

## 🧪 Testing

The project includes automated verification across all layers:

```bash
# 1. Run database tests (69 tests covering schema, CRUD, triggers, constraints)
python tests/test_database.py

# 2. Run AI engine tests (11 tests covering embeddings, ChromaDB, PDF extraction)
python tests/test_ai_engine.py

# 3. Run full end-to-end integration test
python tests/integration_test.py
```

---

## 📄 License
Academic Mini Project for DBMS Coursework.
