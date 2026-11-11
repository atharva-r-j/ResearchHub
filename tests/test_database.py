"""
ResearchHub Database Test Suite
Verifies every database function, SQL feature, and DBMS concept.
Run: python -m tests.test_database  (from the ResearchHub root)
"""

import sys
import os

# Ensure project root is on the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import (
    get_connection,
    add_paper,
    get_paper,
    get_papers_by_ids,
    get_all_papers,
    search_papers,
    update_paper,
    delete_paper,
    add_citation,
    get_cited_papers,
    get_citing_papers,
    add_bookmark,
    remove_bookmark,
    get_user_bookmarks,
    set_reading_status,
    get_user_reading_list,
    get_dashboard_stats,
    get_domain_stats,
    get_top_cited_papers,
    get_user_activity_summary,
)

PASS = 0
FAIL = 0


def check(test_name, condition, detail=""):
    """Simple pass/fail checker with colored output."""
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {test_name}")
    else:
        FAIL += 1
        print(f"  ❌ {test_name}  -->  {detail}")


def heading(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================================
# TEST 1: DATABASE CONNECTION
# ============================================================================
def test_connection():
    heading("TEST 1: Database Connection")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_database();")
    db_name = cur.fetchone()[0]
    check("Connected to researchhub", db_name == "researchhub", f"Got: {db_name}")
    cur.close()
    conn.close()


# ============================================================================
# TEST 2: TABLES EXIST (Schema)
# ============================================================================
def test_tables_exist():
    heading("TEST 2: All 7 Tables Exist (schema.sql)")
    expected = {"users", "papers", "authors", "paper_authors",
                "citations", "bookmarks", "reading_status"}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    actual = {row[0] for row in cur.fetchall()}
    for table in sorted(expected):
        check(f"Table '{table}' exists", table in actual, f"Missing from database")
    cur.close()
    conn.close()


# ============================================================================
# TEST 3: SAMPLE DATA COUNTS
# ============================================================================
def test_sample_data():
    heading("TEST 3: Sample Data Loaded (sample_data.sql)")
    conn = get_connection()
    cur = conn.cursor()
    counts = {}
    for table in ["users", "papers", "authors", "paper_authors",
                   "citations", "bookmarks", "reading_status"]:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        counts[table] = cur.fetchone()[0]

    check("Users >= 3",         counts["users"] >= 3,         f"Got: {counts['users']}")
    check("Papers >= 12",       counts["papers"] >= 12,       f"Got: {counts['papers']}")
    check("Authors >= 12",      counts["authors"] >= 12,      f"Got: {counts['authors']}")
    check("Paper_Authors >= 23", counts["paper_authors"] >= 23, f"Got: {counts['paper_authors']}")
    check("Citations >= 14",    counts["citations"] >= 14,    f"Got: {counts['citations']}")
    check("Bookmarks >= 6",     counts["bookmarks"] >= 6,     f"Got: {counts['bookmarks']}")
    check("Reading_Status >= 6", counts["reading_status"] >= 6, f"Got: {counts['reading_status']}")
    cur.close()
    conn.close()


# ============================================================================
# TEST 4: CRUD OPERATIONS (add, get, update, delete with Transaction)
# ============================================================================
def test_crud():
    heading("TEST 4: CRUD Operations + Transaction (db.py)")

    # CREATE (Transaction: inserts into papers + authors + paper_authors atomically)
    new_id = add_paper({
        "title": "Test Paper: Neural Network Pruning Strategies",
        "abstract": "A survey of pruning methods for deep neural networks.",
        "publication_year": 2025,
        "domain": "Machine Learning",
        "pdf_path": "data/papers/test_pruning.pdf",
        "authors": [
            {"name": "Test Author Alpha", "affiliation": "Test University"},
            "Test Author Beta",
        ],
    })
    check("add_paper() returned integer ID", isinstance(new_id, int) and new_id > 0, f"Got: {new_id}")

    # READ
    paper = get_paper(new_id)
    check("get_paper() returns correct title", paper["title"] == "Test Paper: Neural Network Pruning Strategies")
    check("get_paper() includes 2 authors", len(paper["authors"]) == 2, f"Got: {paper['authors']}")
    check("Authors are in correct order", paper["authors"][0] == "Test Author Alpha")
    check("Domain stored correctly", paper["domain"] == "Machine Learning")

    # UPDATE
    updated = update_paper(new_id, {"title": "Updated: Pruning Strategies v2", "publication_year": 2026})
    check("update_paper() returns True", updated is True)
    paper2 = get_paper(new_id)
    check("Title actually changed", paper2["title"] == "Updated: Pruning Strategies v2")
    check("Year actually changed", paper2["publication_year"] == 2026)

    # DELETE (CASCADE should clean up paper_authors too)
    deleted = delete_paper(new_id)
    check("delete_paper() returns True", deleted is True)
    check("get_paper() returns None after delete", get_paper(new_id) is None)

    # Clean up test authors
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM authors WHERE name LIKE 'Test Author%';")
    conn.commit()
    cur.close()
    conn.close()


# ============================================================================
# TEST 5: KEYWORD SEARCH (search_papers with filters)
# ============================================================================
def test_search():
    heading("TEST 5: Keyword Search (search_papers)")

    # Search by title
    results = search_papers({"title": "radar"})
    check("title='radar' finds >= 2 papers", len(results) >= 2, f"Got: {len(results)}")

    # Search by author
    results = search_papers({"author": "Hinton"})
    titles = [r["title"] for r in results]
    check("author='Hinton' finds AlexNet", any("ImageNet" in t for t in titles), f"Got: {titles}")

    # Search by year + domain combo
    results = search_papers({"publication_year": 2019, "domain": "Natural Language Processing"})
    check("year=2019 + domain=NLP finds 2 papers", len(results) == 2, f"Got: {len(results)}")

    # Search by keyword in abstract
    results = search_papers({"keyword": "adversarial"})
    check("keyword='adversarial' finds GANs paper", len(results) >= 1, f"Got: {len(results)}")

    # Empty filters return all papers
    results = search_papers({})
    check("Empty filters return all 12 papers", len(results) >= 12, f"Got: {len(results)}")


# ============================================================================
# TEST 6: get_papers_by_ids (AI Integration Bridge)
# ============================================================================
def test_get_papers_by_ids():
    heading("TEST 6: get_papers_by_ids (AI Module Integration)")

    # Order preservation is critical for semantic search ranking
    results = get_papers_by_ids([6, 1, 5])
    ids_returned = [r["paper_id"] for r in results]
    check("Returns papers in requested order [6, 1, 5]", ids_returned == [6, 1, 5], f"Got: {ids_returned}")
    check("Each paper has authors list", all(isinstance(r["authors"], list) for r in results))
    check("Each paper has title", all(r["title"] for r in results))

    # Empty input
    check("Empty list returns empty list", get_papers_by_ids([]) == [])

    # Non-existent IDs silently skipped
    results = get_papers_by_ids([9999, 1])
    check("Non-existent ID 9999 skipped gracefully", len(results) == 1 and results[0]["paper_id"] == 1)


# ============================================================================
# TEST 7: CITATIONS (Self-Referencing Relationship + Subqueries)
# ============================================================================
def test_citations():
    heading("TEST 7: Citations (Self-Referencing + Subqueries)")

    # Check existing citations using subquery functions
    cited = get_cited_papers(5)  # Paper 5 cites papers 2 and 3
    cited_ids = [p["paper_id"] for p in cited]
    check("Paper 5 cites papers 2 and 3", set(cited_ids) == {2, 3}, f"Got: {cited_ids}")

    citing = get_citing_papers(1)  # Papers 4, 7, 8 cite paper 1
    citing_ids = [p["paper_id"] for p in citing]
    check("Papers 4, 7, 8 cite paper 1", set(citing_ids) == {4, 7, 8}, f"Got: {citing_ids}")

    # Self-citation blocked
    result = add_citation(1, 1)
    check("Self-citation (1 -> 1) blocked", result is False)

    # Duplicate citation blocked
    result = add_citation(4, 1)  # Already exists in sample data
    check("Duplicate citation (4 -> 1) blocked", result is False)


# ============================================================================
# TEST 8: TRIGGERS (citation_count auto-update)
# ============================================================================
def test_triggers():
    heading("TEST 8: Triggers (Auto Citation Count)")

    paper_before = get_paper(10)  # AlexNet
    count_before = paper_before["citation_count"]

    # Add a new citation: Paper 3 -> Paper 10
    added = add_citation(3, 10)
    check("Added new citation (3 -> 10)", added is True)

    paper_after = get_paper(10)
    check("citation_count incremented by trigger",
          paper_after["citation_count"] == count_before + 1,
          f"Before: {count_before}, After: {paper_after['citation_count']}")

    # Remove the test citation
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM citations WHERE citing_paper_id = 3 AND cited_paper_id = 10;")
    conn.commit()
    cur.close()
    conn.close()

    paper_restored = get_paper(10)
    check("citation_count decremented after delete",
          paper_restored["citation_count"] == count_before,
          f"Expected: {count_before}, Got: {paper_restored['citation_count']}")


# ============================================================================
# TEST 9: BOOKMARKS & READING STATUS
# ============================================================================
def test_bookmarks_and_reading():
    heading("TEST 9: Bookmarks & Reading Status")

    # Test bookmark
    added = add_bookmark(2, 1)
    check("Bookmark added (user 2, paper 1)", added is True)

    bookmarks = get_user_bookmarks(2)
    bk_ids = [b["paper_id"] for b in bookmarks]
    check("User 2 bookmarks include paper 1", 1 in bk_ids, f"Got: {bk_ids}")

    # Duplicate bookmark blocked
    added_again = add_bookmark(2, 1)
    check("Duplicate bookmark blocked", added_again is False)

    # Remove bookmark
    removed = remove_bookmark(2, 1)
    check("Bookmark removed", removed is True)

    # Test reading status
    set_reading_status(3, 5, "reading")
    reading = get_user_reading_list(3)
    statuses = {r["paper_id"]: r["reading_status"] for r in reading}
    check("Reading status set to 'reading'", statuses.get(5) == "reading", f"Got: {statuses}")

    # Update reading status (UPSERT)
    set_reading_status(3, 5, "completed")
    reading2 = get_user_reading_list(3)
    statuses2 = {r["paper_id"]: r["reading_status"] for r in reading2}
    check("Reading status updated to 'completed'", statuses2.get(5) == "completed")

    # Filter by status
    completed_only = get_user_reading_list(3, status="completed")
    check("Filter by status='completed' works", all(r["reading_status"] == "completed" for r in completed_only))

    # Clean up
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reading_status WHERE user_id = 3 AND paper_id = 5;")
    conn.commit()
    cur.close()
    conn.close()


# ============================================================================
# TEST 10: VIEWS & STORED FUNCTIONS (Dashboard)
# ============================================================================
def test_dashboard():
    heading("TEST 10: Views & Stored Functions (Dashboard)")

    stats = get_dashboard_stats()
    check("total_papers is 12", stats["total_papers"] == 12, f"Got: {stats['total_papers']}")
    check("total_authors is 12", stats["total_authors"] == 12, f"Got: {stats['total_authors']}")
    check("most_cited_title present", stats.get("most_cited_title") is not None)
    check("avg_citations_per_paper is numeric", isinstance(stats.get("avg_citations_per_paper"), (int, float)))

    domains = get_domain_stats()
    domain_names = [d["domain"] for d in domains]
    check("domain_stats includes NLP", "Natural Language Processing" in domain_names, f"Got: {domain_names}")
    check("domain_stats has paper_count", all("paper_count" in d for d in domains))

    top = get_top_cited_papers(3)
    check("get_top_cited_papers returns 3", len(top) == 3, f"Got: {len(top)}")
    check("Top paper has highest citation_count", top[0]["citation_count"] >= top[1]["citation_count"])

    activity = get_user_activity_summary(1)
    check("User 1 has 3 bookmarks", activity["bookmark_count"] == 3, f"Got: {activity}")
    check("User 1 has 1 completed", activity["completed"] == 1, f"Got: {activity}")


# ============================================================================
# TEST 11: CONSTRAINTS (Database-Level Protection)
# ============================================================================
def test_constraints():
    heading("TEST 11: Constraints (Data Integrity)")
    import psycopg2

    conn = get_connection()
    cur = conn.cursor()

    # CHECK: publication_year must be 1900-2100
    try:
        cur.execute("INSERT INTO papers (title, publication_year) VALUES ('Bad Year', 3000);")
        conn.commit()
        check("CHECK on publication_year rejects 3000", False, "Insert succeeded when it shouldn't")
        cur.execute("DELETE FROM papers WHERE title = 'Bad Year';")
        conn.commit()
    except psycopg2.errors.CheckViolation:
        conn.rollback()
        check("CHECK on publication_year rejects 3000", True)

    # CHECK: reading_status must be one of 3 values
    try:
        cur.execute("INSERT INTO reading_status (user_id, paper_id, status) VALUES (1, 2, 'invalid');")
        conn.commit()
        check("CHECK on status rejects 'invalid'", False, "Insert succeeded when it shouldn't")
        cur.execute("DELETE FROM reading_status WHERE user_id = 1 AND paper_id = 2 AND status = 'invalid';")
        conn.commit()
    except psycopg2.errors.CheckViolation:
        conn.rollback()
        check("CHECK on status rejects 'invalid'", True)

    # UNIQUE: duplicate bookmark blocked
    try:
        cur.execute("INSERT INTO bookmarks (user_id, paper_id) VALUES (1, 1);")
        cur.execute("INSERT INTO bookmarks (user_id, paper_id) VALUES (1, 1);")
        conn.commit()
        check("UNIQUE on bookmark blocks duplicate", False)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        check("UNIQUE on bookmark blocks duplicate", True)

    # FOREIGN KEY: non-existent paper_id rejected
    try:
        cur.execute("INSERT INTO bookmarks (user_id, paper_id) VALUES (1, 99999);")
        conn.commit()
        check("FK rejects non-existent paper_id", False)
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        check("FK rejects non-existent paper_id", True)

    cur.close()
    conn.close()


# ============================================================================
# TEST 12: INDEXES EXIST
# ============================================================================
def test_indexes():
    heading("TEST 12: Indexes (Performance)")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT indexname FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY indexname;
    """)
    idx_names = {row[0] for row in cur.fetchall()}
    check("Index on papers.title exists",            "idx_papers_title" in idx_names, f"Indexes: {idx_names}")
    check("Index on papers.publication_year exists",  "idx_papers_year" in idx_names)
    check("Index on papers.domain exists",            "idx_papers_domain" in idx_names)
    check("Index on authors.name exists",             "idx_authors_name" in idx_names)
    check("Index on citations.citing exists",         "idx_citations_citing" in idx_names)
    check("Index on citations.cited exists",          "idx_citations_cited" in idx_names)
    cur.close()
    conn.close()


# ============================================================================
# RUN ALL TESTS
# ============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ResearchHub Database Test Suite")
    print("=" * 60)

    test_connection()
    test_tables_exist()
    test_sample_data()
    test_crud()
    test_search()
    test_get_papers_by_ids()
    test_citations()
    test_triggers()
    test_bookmarks_and_reading()
    test_dashboard()
    test_constraints()
    test_indexes()

    print(f"\n{'='*60}")
    print(f"  RESULTS:  {PASS} passed,  {FAIL} failed,  {PASS + FAIL} total")
    print(f"{'='*60}")

    if FAIL > 0:
        sys.exit(1)
