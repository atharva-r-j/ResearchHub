"""
ResearchHub – Minimalist Frontend
A clean, distraction-free interface for research paper management,
relational search (PostgreSQL), and vector semantic search (ChromaDB).
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

# --- Database Layer ---
from database.db import (
    add_paper,
    get_paper,
    get_all_papers,
    search_papers,
    get_papers_by_ids,
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
    authenticate_user,
    register_user,
)

# --- AI Engine Layer ---
try:
    from ai_engine.semantic_search import (
        index_paper as ai_index_paper,
        index_papers_batch as ai_index_papers_batch,
        semantic_search as ai_semantic_search,
        get_similar_papers as ai_get_similar_papers,
        delete_paper_embedding as ai_delete_paper_embedding,
    )
    from ai_engine.pdf_processor import extract_text_from_pdf
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION & MINIMALIST STYLING
# ============================================================================
st.set_page_config(
    page_title="ResearchHub",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimalist CSS: Clean typography, subtle borders, no flashy gradients
st.markdown("""
<style>
/* Font & Base Layout */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px;
}

/* Minimal Header */
.app-header {
    border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    padding-bottom: 14px;
    margin-bottom: 24px;
}
.app-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
}
.app-subtitle {
    font-size: 0.85rem;
    color: #888888;
    margin-top: 4px;
}

/* Minimal Metadata Tag */
.meta-tag {
    display: inline-block;
    padding: 2px 8px;
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 4px;
    font-size: 0.75rem;
    color: inherit;
    opacity: 0.85;
    margin-right: 6px;
    margin-top: 4px;
}

/* Clean Paper Item */
.paper-row {
    border-bottom: 1px solid rgba(128, 128, 128, 0.15);
    padding: 14px 0;
}
.paper-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 4px;
}
.paper-meta {
    font-size: 0.82rem;
    opacity: 0.75;
    margin-bottom: 6px;
}

/* Minimal Metric */
div[data-testid="stMetric"] {
    background: transparent !important;
    border: 1px solid rgba(128, 128, 128, 0.2) !important;
    border-radius: 6px !important;
    padding: 12px 16px !important;
    box-shadow: none !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    opacity: 0.7 !important;
}
div[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

/* Sidebar Clean Styling */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.15) !important;
}
.sidebar-brand {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 2px;
}
.sidebar-sub {
    font-size: 0.75rem;
    opacity: 0.6;
    margin-bottom: 16px;
}
.sidebar-section {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.5;
    margin: 18px 0 6px 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOGIN / REGISTER WALL
# Shows the login page until the user is authenticated. Once logged in,
# the user object is stored in st.session_state["user"] and the full app
# becomes accessible.
# ============================================================================
if "user" not in st.session_state:
    st.session_state["user"] = None

def show_login_page():
    """Render the centered login / register page."""
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown(
            """
            <div style="text-align:center; padding: 2rem 0 1.5rem 0;">
                <div style="font-size:3rem;">📚</div>
                <h1 style="font-size:1.9rem; font-weight:800; letter-spacing:-0.03em; margin:0.4rem 0 0.2rem 0;">
                    ResearchHub
                </h1>
                <p style="opacity:0.55; font-size:0.9rem; margin:0;">
                    AI-Powered Research Paper Management
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        # ── LOGIN TAB ──────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                username_in = st.text_input("Username", placeholder="your_username")
                password_in = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if not username_in.strip() or not password_in:
                    st.error("Please fill in both fields.")
                else:
                    user = authenticate_user(username_in.strip(), password_in)
                    if user:
                        st.session_state["user"] = user
                        st.success(f"Welcome back, {user['full_name'].split()[0]}!")
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")

            st.markdown(
                "<p style='text-align:center; font-size:0.78rem; opacity:0.5; margin-top:0.8rem;'>"
                "Demo — username: <b>atharva_j</b> &nbsp;|&nbsp; password: <b>password123</b>"
                "</p>",
                unsafe_allow_html=True,
            )

        # ── REGISTER TAB ───────────────────────────────────────────────────
        with tab_register:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=True):
                reg_name     = st.text_input("Full Name",        placeholder="Atharva Jadhav")
                reg_username = st.text_input("Username",         placeholder="atharva_j")
                reg_email    = st.text_input("Email",            placeholder="atharva@example.com")
                reg_password = st.text_input("Password",         type="password", placeholder="••••••••")
                reg_confirm  = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                reg_submit   = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if reg_submit:
                if not all([reg_name, reg_username, reg_email, reg_password, reg_confirm]):
                    st.error("Please fill in all fields.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    new_user = register_user(reg_username, reg_email, reg_name, reg_password)
                    if new_user:
                        st.session_state["user"] = new_user
                        st.success(f"Account created! Welcome, {new_user['full_name'].split()[0]}!")
                        st.rerun()
                    else:
                        st.error("Username or email already taken. Try a different one.")

# If not logged in, show login page and stop rendering the rest of the app
if st.session_state["user"] is None:
    show_login_page()
    st.stop()

# Logged-in user shorthand used throughout the app
_current_user: dict = st.session_state["user"]

# ============================================================================
# SIDEBAR NAVIGATION & USER CONTEXT
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">ResearchHub</div>
    <div class="sidebar-sub">DBMS & Vector Search</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Search",
            "Add Paper",
            "Paper Details",
            "Bookmarks",
            "Reading List",
            "Citations",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section">Signed In As</div>', unsafe_allow_html=True)
    st.caption(f"👤 {_current_user['full_name']}")
    st.caption(f"@{_current_user['username']}")
    current_user_id: int = _current_user["user_id"]
    if st.button("Sign Out", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()

    st.markdown('<div class="sidebar-section">AI Engine</div>', unsafe_allow_html=True)
    if AI_AVAILABLE:
        st.caption("ChromaDB · all-MiniLM-L6-v2")
        if st.button("Sync Vector Store", use_container_width=True):
            all_papers = get_all_papers()
            count = ai_index_papers_batch(all_papers)
            st.success(f"Indexed {count} papers")
    else:
        st.caption("AI module not loaded")


# ============================================================================
# HELPER: Minimal Paper Card
# ============================================================================
def render_paper(paper, show_view_button=True):
    """Render a clean, minimal paper row."""
    with st.container():
        col_content, col_action = st.columns([5, 1])

        with col_content:
            st.markdown(f"**{paper['title']}**")

            # Authors line
            authors = paper.get("authors", [])
            authors_str = ", ".join(authors) if isinstance(authors, list) else str(authors or "")
            if authors_str:
                st.caption(authors_str)

            # Metadata tags
            tags = []
            if paper.get("domain"):
                tags.append(f"<span class='meta-tag'>{paper['domain']}</span>")
            if paper.get("publication_year"):
                tags.append(f"<span class='meta-tag'>{paper['publication_year']}</span>")
            if paper.get("citation_count") is not None:
                tags.append(f"<span class='meta-tag'>{paper['citation_count']} citations</span>")
            if paper.get("score") is not None:
                tags.append(f"<span class='meta-tag'>{paper['score']:.1%} match</span>")

            if tags:
                st.markdown("".join(tags), unsafe_allow_html=True)

        with col_action:
            if show_view_button:
                pid = paper["paper_id"]
                if st.button("View", key=f"v_{pid}", use_container_width=True):
                    st.session_state["view_paper_id"] = pid
                    st.rerun()

        if paper.get("abstract"):
            with st.expander("Abstract"):
                st.write(paper["abstract"])

        st.markdown("<hr style='margin: 10px 0; opacity: 0.15;'/>", unsafe_allow_html=True)


# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================
if page == "Dashboard":
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Dashboard</h1>
        <div class="app-subtitle">Overview of repository statistics and personal progress.</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        stats = get_dashboard_stats()
    except Exception as e:
        st.error(f"Database error: {e}")
        st.stop()

    # Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Papers", stats.get("total_papers", 0))
    m2.metric("Authors", stats.get("total_authors", 0))
    m3.metric("Users", stats.get("total_users", 0))
    m4.metric("Citations", stats.get("total_citations", 0))
    m5.metric("Avg Citations", f"{stats.get('avg_citations_per_paper', 0):.1f}")

    st.write("")
    col_top, col_chart = st.columns([1, 1])

    with col_top:
        st.subheader("Top Cited Papers")
        top_papers = get_top_cited_papers(5)
        for i, tp in enumerate(top_papers, 1):
            st.markdown(f"**{i}. {tp['title']}**")
            st.caption(f"{tp['authors']} · {tp['citation_count']} citations")
            st.write("")

    with col_chart:
        st.subheader("Papers by Domain")
        domains = get_domain_stats()
        if domains:
            df = pd.DataFrame(domains)
            st.bar_chart(df.set_index("domain")["paper_count"])

    st.write("")
    st.subheader(f"Activity for {users[current_user_id]}")
    act = get_user_activity_summary(current_user_id)
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Bookmarks", act.get("bookmark_count", 0))
    a2.metric("Want to Read", act.get("want_to_read", 0))
    a3.metric("Reading", act.get("reading", 0))
    a4.metric("Completed", act.get("completed", 0))


# ============================================================================
# PAGE 2: SEARCH
# ============================================================================
elif page == "Search":
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Search</h1>
        <div class="app-subtitle">Explore papers using natural language semantic search or SQL filters.</div>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Search Mode", ["Semantic Search (AI)", "Keyword & Filters (SQL)"], horizontal=True)

    if mode == "Semantic Search (AI)":
        if not AI_AVAILABLE:
            st.warning("AI engine not available. Install sentence-transformers and chromadb.")
        else:
            query = st.text_input("Semantic Query", placeholder="e.g. radar signal denoising or transformer architectures")
            top_k = st.slider("Results limit", 1, 20, 5)

            if st.button("Search", type="primary") and query.strip():
                with st.spinner("Searching vector space..."):
                    try:
                        results = ai_semantic_search(query.strip(), top_k=top_k)
                        if results:
                            ids = [r["paper_id"] for r in results]
                            scores = {r["paper_id"]: r["score"] for r in results}
                            papers = get_papers_by_ids(ids)
                            st.write(f"Found {len(papers)} papers:")
                            for p in papers:
                                p["score"] = scores.get(p["paper_id"])
                                render_paper(p)
                        else:
                            st.info("No matching papers found. Try syncing vector store in the sidebar.")
                    except Exception as e:
                        st.error(f"Search failed: {e}")

    else:
        c1, c2 = st.columns(2)
        with c1:
            title_filter = st.text_input("Title")
            author_filter = st.text_input("Author")
        with c2:
            year_filter = st.text_input("Year")
            domain_filter = st.text_input("Domain")
        keyword_filter = st.text_input("Keyword in title/abstract")

        if st.button("Filter Papers", type="primary"):
            filters = {}
            if title_filter.strip():
                filters["title"] = title_filter.strip()
            if author_filter.strip():
                filters["author"] = author_filter.strip()
            if year_filter.strip():
                try:
                    filters["publication_year"] = int(year_filter.strip())
                except ValueError:
                    pass
            if domain_filter.strip():
                filters["domain"] = domain_filter.strip()
            if keyword_filter.strip():
                filters["keyword"] = keyword_filter.strip()

            results = search_papers(filters)
            st.write(f"Found {len(results)} papers:")
            for p in results:
                render_paper(p)


# ============================================================================
# PAGE 3: ADD PAPER
# ============================================================================
elif page == "Add Paper":
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Add Paper</h1>
        <div class="app-subtitle">Upload a PDF or enter paper metadata manually.</div>
    </div>
    """, unsafe_allow_html=True)

    pdf_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
    extracted_abstract = ""
    saved_path = None

    if pdf_file:
        papers_dir = PROJECT_ROOT / "data" / "papers"
        papers_dir.mkdir(parents=True, exist_ok=True)
        dest = papers_dir / pdf_file.name
        with open(dest, "wb") as f:
            f.write(pdf_file.getbuffer())
        saved_path = f"data/papers/{pdf_file.name}"

        if AI_AVAILABLE:
            text = extract_text_from_pdf(dest)
            if text:
                extracted_abstract = text[:1000].strip()
                st.caption(f"Extracted {len(text)} characters from PDF.")

    with st.form("new_paper_form"):
        title = st.text_input("Title *")
        abstract = st.text_area("Abstract", value=extracted_abstract, height=120)
        c1, c2 = st.columns(2)
        with c1:
            year = st.number_input("Publication Year", min_value=1900, max_value=2100, value=2024)
        with c2:
            domain = st.text_input("Domain")
        authors = st.text_input("Authors (comma-separated)")
        pdf_path = st.text_input("PDF Path", value=saved_path or "")

        submit = st.form_submit_button("Add Paper", type="primary")

    if submit:
        if not title.strip():
            st.error("Title is required.")
        else:
            paper_data = {
                "title": title.strip(),
                "abstract": abstract.strip() or None,
                "publication_year": year,
                "domain": domain.strip() or None,
                "pdf_path": pdf_path.strip() or None,
                "authors": [a.strip() for a in authors.split(",") if a.strip()],
            }
            try:
                pid = add_paper(paper_data)
                st.success(f"Paper added with ID: {pid}")
                if AI_AVAILABLE and (paper_data["title"] or paper_data["abstract"]):
                    try:
                        ai_index_paper(pid, paper_data["title"], paper_data["abstract"] or "")
                    except Exception as e:
                        st.warning(f"Saved to DB, but vector indexing failed: {e}")
            except Exception as e:
                st.error(f"Error adding paper: {e}")


# ============================================================================
# PAGE 4: PAPER DETAILS
# ============================================================================
elif page == "Paper Details":
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Paper Details</h1>
        <div class="app-subtitle">Inspect metadata, citations, reading state, and similar papers.</div>
    </div>
    """, unsafe_allow_html=True)

    default_pid = st.session_state.get("view_paper_id", 1)
    paper_id = st.number_input("Paper ID", min_value=1, value=default_pid, step=1)

    paper = get_paper(paper_id)
    if not paper:
        st.warning(f"Paper ID {paper_id} not found.")
    else:
        st.subheader(paper["title"])
        authors = paper.get("authors", [])
        if authors:
            st.caption(f"Authors: {', '.join(authors)}")

        # Info line
        st.write(f"**Year:** {paper.get('publication_year', 'N/A')} · **Domain:** {paper.get('domain', 'N/A')} · **Citations:** {paper.get('citation_count', 0)}")

        if paper.get("abstract"):
            st.markdown("**Abstract**")
            st.write(paper["abstract"])

        st.write("")

        # Actions Row
        c_bk, c_rd = st.columns(2)
        with c_bk:
            st.markdown("**Bookmarks**")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Add Bookmark", use_container_width=True):
                    if add_bookmark(current_user_id, paper_id):
                        st.success("Bookmarked")
                    else:
                        st.info("Already bookmarked")
            with b2:
                if st.button("Remove Bookmark", use_container_width=True):
                    if remove_bookmark(current_user_id, paper_id):
                        st.success("Removed")
                    else:
                        st.info("Not bookmarked")

        with c_rd:
            st.markdown("**Reading Status**")
            s1, s2 = st.columns([2, 1])
            with s1:
                status = st.selectbox(
                    "Status",
                    ["want_to_read", "reading", "completed"],
                    format_func=lambda s: s.replace("_", " ").title(),
                    label_visibility="collapsed",
                )
            with s2:
                if st.button("Set", use_container_width=True):
                    set_reading_status(current_user_id, paper_id, status)
                    st.success("Updated")

        st.write("")
        st.markdown("<hr style='opacity: 0.2;'/>", unsafe_allow_html=True)

        # Citations
        c_ref, c_cited = st.columns(2)
        with c_ref:
            st.markdown("**References (Outbound Citations)**")
            cited = get_cited_papers(paper_id)
            if cited:
                for c in cited:
                    st.write(f"- [{c['paper_id']}] {c['title']} ({c.get('publication_year', 'N/A')})")
            else:
                st.caption("No references recorded.")

        with c_cited:
            st.markdown("**Cited By (Inbound Citations)**")
            citing = get_citing_papers(paper_id)
            if citing:
                for c in citing:
                    st.write(f"- [{c['paper_id']}] {c['title']} ({c.get('publication_year', 'N/A')})")
            else:
                st.caption("No inbound citations.")

        # Recommendations
        if AI_AVAILABLE:
            st.write("")
            st.markdown("<hr style='opacity: 0.2;'/>", unsafe_allow_html=True)
            st.markdown("**Similar Papers (AI Recommendation)**")
            if st.button("Find Similar Papers"):
                with st.spinner("Finding nearest neighbors in vector space..."):
                    try:
                        sim = ai_get_similar_papers(paper_id, top_k=5)
                        if sim:
                            sim_ids = [s["paper_id"] for s in sim]
                            scores = {s["paper_id"]: s["score"] for s in sim}
                            sim_papers = get_papers_by_ids(sim_ids)
                            for sp in sim_papers:
                                sp["score"] = scores.get(sp["paper_id"])
                                render_paper(sp, show_view_button=True)
                        else:
                            st.info("No similar papers found.")
                    except Exception as e:
                        st.error(f"Recommendation error: {e}")

        # Delete
        st.write("")
        with st.expander("Delete Paper"):
            st.warning("Deleting this paper will remove its citations, bookmarks, and vector embedding.")
            if st.button("Delete Paper", type="secondary"):
                if delete_paper(paper_id):
                    if AI_AVAILABLE:
                        try:
                            ai_delete_paper_embedding(paper_id)
                        except Exception:
                            pass
                    st.success("Paper deleted.")
                else:
                    st.error("Failed to delete paper.")


# ============================================================================
# PAGE 5: BOOKMARKS
# ============================================================================
elif page == "Bookmarks":
    st.markdown(f"""
    <div class="app-header">
        <h1 class="app-title">Bookmarks</h1>
        <div class="app-subtitle">Saved publications for {users[current_user_id]}.</div>
    </div>
    """, unsafe_allow_html=True)

    bks = get_user_bookmarks(current_user_id)
    if bks:
        st.write(f"{len(bks)} bookmarked papers:")
        for p in bks:
            render_paper(p)
    else:
        st.info("No bookmarks saved.")


# ============================================================================
# PAGE 6: READING LIST
# ============================================================================
elif page == "Reading List":
    st.markdown(f"""
    <div class="app-header">
        <h1 class="app-title">Reading List</h1>
        <div class="app-subtitle">Reading pipeline for {users[current_user_id]}.</div>
    </div>
    """, unsafe_allow_html=True)

    status_filter = st.selectbox(
        "Filter status",
        [None, "want_to_read", "reading", "completed"],
        format_func=lambda x: "All Statuses" if x is None else x.replace("_", " ").title(),
    )

    items = get_user_reading_list(current_user_id, status=status_filter)
    if items:
        for p in items:
            st.caption(f"Status: {p.get('reading_status', '').replace('_', ' ').title()}")
            render_paper(p)
    else:
        st.info("No papers found in this category.")


# ============================================================================
# PAGE 7: CITATIONS EXPLORER
# ============================================================================
elif page == "Citations":
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">Citations Explorer</h1>
        <div class="app-subtitle">Create citation links and traverse citation trees.</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Add Citation Link")
    with st.form("add_cite_form"):
        c1, c2 = st.columns(2)
        with c1:
            citing = st.number_input("Citing Paper ID", min_value=1, value=1, step=1)
        with c2:
            cited = st.number_input("Cited Paper ID", min_value=1, value=2, step=1)
        sub = st.form_submit_button("Add Citation Edge")

    if sub:
        if citing == cited:
            st.error("A paper cannot cite itself.")
        else:
            if add_citation(citing, cited):
                st.success(f"Citation created: Paper {citing} → Paper {cited}")
            else:
                st.warning("Citation already exists or IDs are invalid.")

    st.write("")
    st.subheader("Inspect Paper Network")
    target_id = st.number_input("Paper ID to inspect", min_value=1, value=1, step=1)

    p = get_paper(target_id)
    if p:
        st.markdown(f"**{p['title']}** ({p.get('citation_count', 0)} citations)")
        col_ref, col_cited = st.columns(2)
        with col_ref:
            st.write("**References (Outgoing):**")
            refs = get_cited_papers(target_id)
            if refs:
                for r in refs:
                    st.write(f"- [{r['paper_id']}] {r['title']}")
            else:
                st.caption("None.")
        with col_cited:
            st.write("**Cited By (Incoming):**")
            cits = get_citing_papers(target_id)
            if cits:
                for c in cits:
                    st.write(f"- [{c['paper_id']}] {c['title']}")
            else:
                st.caption("None.")
    else:
        st.warning(f"Paper {target_id} not found.")
