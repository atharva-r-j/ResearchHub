-- ============================================================================
-- ResearchHub Database Triggers
-- Step 6: Automatic citation_count maintenance & updated_at timestamps
-- ============================================================================

-- ============================================================================
-- 1. CITATION COUNT TRIGGER
-- Automatically increments/decrements papers.citation_count whenever rows
-- are inserted into, updated in, or deleted from the citations table.
-- ============================================================================
CREATE OR REPLACE FUNCTION update_citation_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE papers
        SET citation_count = citation_count + 1
        WHERE paper_id = NEW.cited_paper_id;
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE papers
        SET citation_count = GREATEST(citation_count - 1, 0)
        WHERE paper_id = OLD.cited_paper_id;
        RETURN OLD;

    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.cited_paper_id <> NEW.cited_paper_id THEN
            UPDATE papers
            SET citation_count = GREATEST(citation_count - 1, 0)
            WHERE paper_id = OLD.cited_paper_id;

            UPDATE papers
            SET citation_count = citation_count + 1
            WHERE paper_id = NEW.cited_paper_id;
        END IF;
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_citation_count ON citations;
CREATE TRIGGER trg_citation_count
AFTER INSERT OR DELETE OR UPDATE ON citations
FOR EACH ROW
EXECUTE FUNCTION update_citation_count();

-- ============================================================================
-- 2. UPDATED_AT TIMESTAMP TRIGGER
-- Automatically sets updated_at = NOW() before a row is modified.
-- ============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_papers_updated_at ON papers;
CREATE TRIGGER trg_papers_updated_at
BEFORE UPDATE ON papers
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_reading_status_updated_at ON reading_status;
CREATE TRIGGER trg_reading_status_updated_at
BEFORE UPDATE ON reading_status
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================================
-- 3. INITIAL SYNC FOR EXISTING SAMPLE DATA
-- Sync citation_count for citations that were inserted before this trigger
-- was created. Future inserts/deletes are handled automatically by the trigger.
-- ============================================================================
UPDATE papers p
SET citation_count = (
    SELECT COUNT(*)
    FROM citations c
    WHERE c.cited_paper_id = p.paper_id
);

