-- ============================================================================
-- ResearchHub Database Schema
-- Step 2: Create all 7 tables, primary keys, foreign keys, constraints & indexes
-- ============================================================================

-- Drop existing tables (in reverse order of dependencies) so this script
-- can be re-run cleanly during development/testing.
DROP TABLE IF EXISTS reading_status CASCADE;
DROP TABLE IF EXISTS bookmarks CASCADE;
DROP TABLE IF EXISTS citations CASCADE;
DROP TABLE IF EXISTS paper_authors CASCADE;
DROP TABLE IF EXISTS authors CASCADE;
DROP TABLE IF EXISTS papers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- 1. USERS TABLE
-- Stores students / researchers using the system.
-- ============================================================================
CREATE TABLE users (
    user_id     SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    full_name     VARCHAR(100) NOT NULL,
    password_hash VARCHAR(64)  NOT NULL DEFAULT '',
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 2. PAPERS TABLE
-- Core table storing metadata for each research paper.
-- Note: paper_id is the shared key linking PostgreSQL and ChromaDB.
-- ============================================================================
CREATE TABLE papers (
    paper_id          SERIAL PRIMARY KEY,
    title             VARCHAR(500) NOT NULL,
    abstract          TEXT,
    publication_year  INTEGER CHECK (publication_year BETWEEN 1900 AND 2100),
    domain            VARCHAR(100),
    pdf_path          VARCHAR(500),
    citation_count    INTEGER NOT NULL DEFAULT 0 CHECK (citation_count >= 0),
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. AUTHORS TABLE
-- Stores unique authors separately (Normalization: avoids comma-separated names).
-- ============================================================================
CREATE TABLE authors (
    author_id    SERIAL PRIMARY KEY,
    name         VARCHAR(200) NOT NULL,
    affiliation  VARCHAR(300)
);

-- ============================================================================
-- 4. PAPER_AUTHORS TABLE (Junction / Bridge Table)
-- Connects Papers and Authors (Many-to-Many relationship).
-- author_order tracks 1st author, 2nd author, etc.
-- ============================================================================
CREATE TABLE paper_authors (
    paper_id      INTEGER NOT NULL REFERENCES papers(paper_id)   ON DELETE CASCADE,
    author_id     INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE CASCADE,
    author_order  INTEGER NOT NULL CHECK (author_order >= 1),
    PRIMARY KEY (paper_id, author_id)
);

-- ============================================================================
-- 5. CITATIONS TABLE (Self-Referencing Relationship)
-- Tracks which paper cites which paper (both FKs point to papers).
-- ============================================================================
CREATE TABLE citations (
    citation_id      SERIAL PRIMARY KEY,
    citing_paper_id  INTEGER NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    cited_paper_id   INTEGER NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_citation_pair UNIQUE (citing_paper_id, cited_paper_id),
    CONSTRAINT chk_no_self_citation CHECK (citing_paper_id <> cited_paper_id)
);

-- ============================================================================
-- 6. BOOKMARKS TABLE
-- Tracks papers saved by users for later reading.
-- ============================================================================
CREATE TABLE bookmarks (
    bookmark_id  SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(user_id)   ON DELETE CASCADE,
    paper_id     INTEGER NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_paper_bookmark UNIQUE (user_id, paper_id)
);

-- ============================================================================
-- 7. READING_STATUS TABLE
-- Tracks a user's reading progress on a paper.
-- ============================================================================
CREATE TABLE reading_status (
    reading_status_id  SERIAL PRIMARY KEY,
    user_id            INTEGER NOT NULL REFERENCES users(user_id)   ON DELETE CASCADE,
    paper_id           INTEGER NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    status             VARCHAR(20) NOT NULL CHECK (status IN ('want_to_read', 'reading', 'completed')),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_paper_status UNIQUE (user_id, paper_id)
);

-- ============================================================================
-- INDEXES (For faster searches on frequently queried columns)
-- ============================================================================
CREATE INDEX idx_papers_title   ON papers (title);
CREATE INDEX idx_papers_year    ON papers (publication_year);
CREATE INDEX idx_papers_domain  ON papers (domain);
CREATE INDEX idx_authors_name   ON authors (name);
CREATE INDEX idx_citations_citing ON citations (citing_paper_id);
CREATE INDEX idx_citations_cited  ON citations (cited_paper_id);

