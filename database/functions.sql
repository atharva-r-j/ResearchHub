-- ============================================================================
-- ResearchHub Stored Functions & Views
-- Step 7: Dashboard statistics views and reusable PostgreSQL stored functions
-- ============================================================================

-- ============================================================================
-- 1. VIEW: dashboard_stats
-- Single-row summary of system-wide counts for the Streamlit dashboard.
-- Uses subqueries to aggregate across multiple tables cleanly.
-- ============================================================================
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM papers)    AS total_papers,
    (SELECT COUNT(*) FROM authors)   AS total_authors,
    (SELECT COUNT(*) FROM users)     AS total_users,
    (SELECT COUNT(*) FROM citations) AS total_citations,
    (SELECT COUNT(*) FROM bookmarks) AS total_bookmarks,
    (
        SELECT title
        FROM papers
        ORDER BY citation_count DESC, paper_id ASC
        LIMIT 1
    ) AS most_cited_title,
    (
        SELECT COALESCE(MAX(citation_count), 0)
        FROM papers
    ) AS highest_citation_count;

-- ============================================================================
-- 2. VIEW: domain_stats
-- Paper count and total citations grouped by research domain.
-- ============================================================================
CREATE OR REPLACE VIEW domain_stats AS
SELECT
    COALESCE(domain, 'Uncategorized') AS domain,
    COUNT(*)                          AS paper_count,
    COALESCE(SUM(citation_count), 0)  AS total_citations
FROM papers
GROUP BY COALESCE(domain, 'Uncategorized')
ORDER BY paper_count DESC, total_citations DESC;

-- ============================================================================
-- 3. STORED FUNCTION: get_paper_statistics()
-- Returns overall repository statistics including average citations.
-- ============================================================================
CREATE OR REPLACE FUNCTION get_paper_statistics()
RETURNS TABLE (
    total_papers            BIGINT,
    total_authors           BIGINT,
    total_citations         BIGINT,
    avg_citations_per_paper NUMERIC(6, 2),
    top_domain              VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM papers),
        (SELECT COUNT(*) FROM authors),
        (SELECT COUNT(*) FROM citations),
        (SELECT COALESCE(ROUND(AVG(citation_count), 2), 0.00) FROM papers),
        (
            SELECT p.domain
            FROM papers p
            WHERE p.domain IS NOT NULL
            GROUP BY p.domain
            ORDER BY COUNT(*) DESC
            LIMIT 1
        );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 4. STORED FUNCTION: get_top_cited_papers(limit_count)
-- Returns the top N most cited papers along with their authors.
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_cited_papers(limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    paper_id         INTEGER,
    title            VARCHAR,
    publication_year INTEGER,
    domain           VARCHAR,
    citation_count   INTEGER,
    authors          TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.paper_id,
        p.title,
        p.publication_year,
        p.domain,
        p.citation_count,
        COALESCE(
            STRING_AGG(a.name, ', ' ORDER BY pa.author_order),
            'Unknown'
        ) AS authors
    FROM papers p
    LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
    LEFT JOIN authors a ON pa.author_id = a.author_id
    GROUP BY p.paper_id
    ORDER BY p.citation_count DESC, p.publication_year DESC, p.paper_id ASC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 5. STORED FUNCTION: get_user_activity_summary(p_user_id)
-- Summarizes a user's bookmarks and reading progress counts.
-- ============================================================================
CREATE OR REPLACE FUNCTION get_user_activity_summary(p_user_id INTEGER)
RETURNS TABLE (
    bookmark_count  BIGINT,
    want_to_read    BIGINT,
    reading         BIGINT,
    completed       BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM bookmarks b WHERE b.user_id = p_user_id),
        (SELECT COUNT(*) FROM reading_status rs WHERE rs.user_id = p_user_id AND rs.status = 'want_to_read'),
        (SELECT COUNT(*) FROM reading_status rs WHERE rs.user_id = p_user_id AND rs.status = 'reading'),
        (SELECT COUNT(*) FROM reading_status rs WHERE rs.user_id = p_user_id AND rs.status = 'completed');
END;
$$ LANGUAGE plpgsql;
