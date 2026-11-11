"""
ResearchHub Database Module (database/db.py)
Provides the Python interface to PostgreSQL for papers, authors,
citations, bookmarks, and reading status.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load .env from the project root regardless of current working directory
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# Shared SELECT query to fetch paper metadata along with ordered author names
_PAPER_SELECT_SQL = """
    SELECT
        p.paper_id,
        p.title,
        p.abstract,
        p.publication_year,
        p.domain,
        p.pdf_path,
        p.citation_count,
        p.created_at,
        p.updated_at,
        COALESCE(
            ARRAY_AGG(a.name ORDER BY pa.author_order)
            FILTER (WHERE a.name IS NOT NULL),
            '{}'
        ) AS authors
    FROM papers p
    LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
    LEFT JOIN authors a ON pa.author_id = a.author_id
"""


def get_connection():
    """Create and return a new PostgreSQL database connection."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def _format_paper_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a database row into the standardized paper dictionary."""
    return {
        "paper_id": row["paper_id"],
        "title": row["title"],
        "abstract": row["abstract"],
        "publication_year": row["publication_year"],
        "domain": row["domain"],
        "pdf_path": row["pdf_path"],
        "citation_count": row["citation_count"],
        "authors": list(row["authors"]) if row["authors"] else [],
    }


def _get_or_create_author(cur, name: str, affiliation: Optional[str] = None) -> int:
    """Return existing author_id by case-insensitive name, or insert a new author."""
    cur.execute(
        "SELECT author_id FROM authors WHERE LOWER(name) = LOWER(%s) LIMIT 1;",
        (name.strip(),),
    )
    existing = cur.fetchone()
    if existing:
        return existing[0]

    cur.execute(
        "INSERT INTO authors (name, affiliation) VALUES (%s, %s) RETURNING author_id;",
        (name.strip(), affiliation),
    )
    return cur.fetchone()[0]


# ============================================================================
# PAPER CRUD OPERATIONS
# ============================================================================

def add_paper(paper_data: Dict[str, Any]) -> int:
    """
    Insert a new paper and its authors inside a single transaction.

    Args:
        paper_data: Dictionary with 'title' (required) and optional keys:
                    'abstract', 'publication_year', 'domain', 'pdf_path', 'authors'.
                    'authors' can be a list of name strings or dicts with 'name'/'affiliation'.

    Returns:
        The newly created paper_id (int).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO papers (title, abstract, publication_year, domain, pdf_path)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING paper_id;
                """,
                (
                    paper_data["title"],
                    paper_data.get("abstract"),
                    paper_data.get("publication_year"),
                    paper_data.get("domain"),
                    paper_data.get("pdf_path"),
                ),
            )
            paper_id = cur.fetchone()[0]

            authors = paper_data.get("authors") or []
            for order, author in enumerate(authors, start=1):
                if isinstance(author, dict):
                    author_name = author["name"]
                    affiliation = author.get("affiliation")
                else:
                    author_name = str(author)
                    affiliation = None

                if not author_name.strip():
                    continue

                author_id = _get_or_create_author(cur, author_name, affiliation)
                cur.execute(
                    """
                    INSERT INTO paper_authors (paper_id, author_id, author_order)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (paper_id, author_id) DO NOTHING;
                    """,
                    (paper_id, author_id, order),
                )

        conn.commit()
        return paper_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_paper(paper_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single paper with its authors by paper_id."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                _PAPER_SELECT_SQL + " WHERE p.paper_id = %s GROUP BY p.paper_id;",
                (paper_id,),
            )
            row = cur.fetchone()
            return _format_paper_row(row) if row else None
    finally:
        conn.close()


def get_papers_by_ids(paper_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Retrieve metadata for a list of paper IDs (used by ChromaDB semantic search).
    Preserves the input ranking order of paper_ids.
    """
    if not paper_ids:
        return []

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                _PAPER_SELECT_SQL + " WHERE p.paper_id = ANY(%s) GROUP BY p.paper_id;",
                (paper_ids,),
            )
            rows = cur.fetchall()
            papers_by_id = {row["paper_id"]: _format_paper_row(row) for row in rows}
            # Preserve the similarity order returned by ChromaDB
            return [papers_by_id[pid] for pid in paper_ids if pid in papers_by_id]
    finally:
        conn.close()


def get_all_papers(limit: int = 100) -> List[Dict[str, Any]]:
    """Return all papers ordered by most recently added."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                _PAPER_SELECT_SQL + " GROUP BY p.paper_id ORDER BY p.paper_id DESC LIMIT %s;",
                (limit,),
            )
            return [_format_paper_row(row) for row in cur.fetchall()]
    finally:
        conn.close()


def search_papers(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Search papers using optional keyword filters.

    Supported filter keys in `filters`:
        - title (str): case-insensitive partial match on paper title
        - author (str): case-insensitive partial match on any author name
        - publication_year (int) or year (int): exact publication year match
        - domain (str): case-insensitive partial match on research domain
        - keyword (str): case-insensitive match in title OR abstract
    """
    filters = filters or {}
    conditions: List[str] = []
    params: List[Any] = []

    if filters.get("title"):
        conditions.append("p.title ILIKE %s")
        params.append(f"%{filters['title'].strip()}%")

    if filters.get("keyword"):
        kw = f"%{filters['keyword'].strip()}%"
        conditions.append("(p.title ILIKE %s OR p.abstract ILIKE %s)")
        params.extend([kw, kw])

    year = filters.get("publication_year") or filters.get("year")
    if year is not None and str(year).strip() != "":
        conditions.append("p.publication_year = %s")
        params.append(int(year))

    if filters.get("domain"):
        conditions.append("p.domain ILIKE %s")
        params.append(f"%{filters['domain'].strip()}%")

    if filters.get("author"):
        conditions.append(
            """
            EXISTS (
                SELECT 1
                FROM paper_authors pa_f
                JOIN authors a_f ON pa_f.author_id = a_f.author_id
                WHERE pa_f.paper_id = p.paper_id
                  AND a_f.name ILIKE %s
            )
            """
        )
        params.append(f"%{filters['author'].strip()}%")

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    query = (
        _PAPER_SELECT_SQL
        + where_clause
        + " GROUP BY p.paper_id ORDER BY p.citation_count DESC, p.publication_year DESC, p.paper_id DESC;"
    )

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [_format_paper_row(row) for row in cur.fetchall()]
    finally:
        conn.close()


def update_paper(paper_id: int, updates: Dict[str, Any]) -> bool:
    """Update allowed fields on a paper. Returns True if a row was updated."""
    allowed_fields = {"title", "abstract", "publication_year", "domain", "pdf_path"}
    fields_to_update = {k: v for k, v in updates.items() if k in allowed_fields}
    if not fields_to_update:
        return False

    set_clauses = [f"{col} = %s" for col in fields_to_update]
    values = list(fields_to_update.values()) + [paper_id]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE papers SET {', '.join(set_clauses)} WHERE paper_id = %s;",
                values,
            )
            updated = cur.rowcount > 0
        conn.commit()
        return updated
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_paper(paper_id: int) -> bool:
    """Delete a paper by ID (cascades to paper_authors, citations, bookmarks)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM papers WHERE paper_id = %s;", (paper_id,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ============================================================================
# CITATION OPERATIONS (Self-Referencing + Subqueries)
# ============================================================================

def add_citation(citing_id: int, cited_id: int) -> bool:
    """
    Record that citing_id cites cited_id.
    Returns True if added, False if invalid (e.g., self-citation or duplicate).
    """
    if citing_id == cited_id:
        return False

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO citations (citing_paper_id, cited_paper_id)
                VALUES (%s, %s)
                ON CONFLICT (citing_paper_id, cited_paper_id) DO NOTHING;
                """,
                (citing_id, cited_id),
            )
            inserted = cur.rowcount > 0
        conn.commit()
        return inserted
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_cited_papers(paper_id: int) -> List[Dict[str, Any]]:
    """Get all papers that this paper cites (its references), using a subquery."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                _PAPER_SELECT_SQL
                + """
                WHERE p.paper_id IN (
                    SELECT cited_paper_id
                    FROM citations
                    WHERE citing_paper_id = %s
                )
                GROUP BY p.paper_id
                ORDER BY p.publication_year DESC;
                """,
                (paper_id,),
            )
            return [_format_paper_row(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_citing_papers(paper_id: int) -> List[Dict[str, Any]]:
    """Get all papers that cite this paper, using a subquery."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                _PAPER_SELECT_SQL
                + """
                WHERE p.paper_id IN (
                    SELECT citing_paper_id
                    FROM citations
                    WHERE cited_paper_id = %s
                )
                GROUP BY p.paper_id
                ORDER BY p.publication_year DESC;
                """,
                (paper_id,),
            )
            return [_format_paper_row(row) for row in cur.fetchall()]
    finally:
        conn.close()


# ============================================================================
# BOOKMARKS & READING STATUS
# ============================================================================

def add_bookmark(user_id: int, paper_id: int) -> bool:
    """Bookmark a paper for a user. Returns True if newly added."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bookmarks (user_id, paper_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, paper_id) DO NOTHING;
                """,
                (user_id, paper_id),
            )
            added = cur.rowcount > 0
        conn.commit()
        return added
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


def remove_bookmark(user_id: int, paper_id: int) -> bool:
    """Remove a bookmark for a user."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM bookmarks WHERE user_id = %s AND paper_id = %s;",
                (user_id, paper_id),
            )
            removed = cur.rowcount > 0
        conn.commit()
        return removed
    finally:
        conn.close()


def get_user_bookmarks(user_id: int) -> List[Dict[str, Any]]:
    """Fetch all papers bookmarked by a user."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                _PAPER_SELECT_SQL
                + """
                INNER JOIN bookmarks b ON p.paper_id = b.paper_id
                WHERE b.user_id = %s
                GROUP BY p.paper_id, b.created_at
                ORDER BY b.created_at DESC;
                """,
                (user_id,),
            )
            return [_format_paper_row(row) for row in cur.fetchall()]
    finally:
        conn.close()


def set_reading_status(user_id: int, paper_id: int, status: str) -> bool:
    """Insert or update reading status ('want_to_read', 'reading', 'completed')."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reading_status (user_id, paper_id, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, paper_id)
                DO UPDATE SET status = EXCLUDED.status, updated_at = NOW();
                """,
                (user_id, paper_id, status),
            )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_reading_list(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch papers on a user's reading list, optionally filtered by status."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = (
                """
                SELECT
                    p.paper_id, p.title, p.abstract, p.publication_year,
                    p.domain, p.pdf_path, p.citation_count,
                    rs.status AS reading_status,
                    COALESCE(
                        ARRAY_AGG(a.name ORDER BY pa.author_order)
                        FILTER (WHERE a.name IS NOT NULL),
                        '{}'
                    ) AS authors
                FROM papers p
                INNER JOIN reading_status rs ON p.paper_id = rs.paper_id
                LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
                LEFT JOIN authors a ON pa.author_id = a.author_id
                WHERE rs.user_id = %s
                """
            )
            params: List[Any] = [user_id]
            if status:
                query += " AND rs.status = %s"
                params.append(status)

            query += " GROUP BY p.paper_id, rs.status, rs.updated_at ORDER BY rs.updated_at DESC;"
            cur.execute(query, params)
            rows = cur.fetchall()
            result = []
            for row in rows:
                paper = _format_paper_row(row)
                paper["reading_status"] = row["reading_status"]
                result.append(paper)
            return result
    finally:
        conn.close()

