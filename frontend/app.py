"""
ResearchHub – Streamlit Frontend
Connects the PostgreSQL database module (database/db.py) with the
AI semantic search module (ai_engine/semantic_search.py).
"""

import sys
import os
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# --- Database imports (your module) ---
from database.db import (
    add_paper,
    get_paper,
    get_all_papers,
    search_papers,
    get_papers_by_ids,
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

# --- AI imports (AI Engine module) ---
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
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="ResearchHub",
    page_icon="📚",
    layout="wide",
)

# ============================================================================
# SIDEBAR – NAVIGATION
# ============================================================================
st.sidebar.title("📚 ResearchHub")
st.sidebar.caption("AI-Powered Research Paper Management")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🔍 Search Papers", "➕ Add Paper", "📄 Paper Details",
     "📑 My Bookmarks", "📖 Reading List", "🔗 Citations Explorer"],
)

if not AI_AVAILABLE:
    st.sidebar.warning("⚠️ AI module not loaded. Semantic search disabled. Install: `pip install sentence-transformers chromadb pymupdf`")
else:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Vector Engine")
    if st.sidebar.button("🔄 Sync All to ChromaDB", use_container_width=True):
        with st.sidebar.status("Indexing all papers into vector DB..."):
            all_papers = get_all_papers()
            count = ai_index_papers_batch(all_papers)
            st.sidebar.success(f"Indexed {count} papers!")

# Simple user selector (no auth – this is a demo project)
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Current User")
current_user_id = st.sidebar.selectbox(
    "Select user",
    [1, 2, 3],
    format_func=lambda uid: {1: "Atharva Jadhav", 2: "Riya Sharma", 3: "Dr. Rajesh Mehta"}.get(uid, f"User {uid}"),
)


# ============================================================================
# HELPER: Display a paper card
# ============================================================================
def paper_card(paper, show_actions=True):
    """Render a paper as a styled card with optional bookmark/reading actions."""
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader(paper["title"])
            authors = paper.get("authors", [])
            if authors:
                st.caption(f"👥 {', '.join(authors) if isinstance(authors, list) else authors}")
            meta_parts = []
            if paper.get("publication_year"):
                meta_parts.append(f"📅 {paper['publication_year']}")
            if paper.get("domain"):
                meta_parts.append(f"🏷️ {paper['domain']}")
            if paper.get("citation_count") is not None:
                meta_parts.append(f"📊 {paper['citation_count']} citations")
            if meta_parts:
                st.markdown(" · ".join(meta_parts))
        with col2:
            if show_actions:
                pid = paper["paper_id"]
                if st.button("📄 View", key=f"view_{pid}"):
                    st.session_state["view_paper_id"] = pid
                    st.rerun()

        if paper.get("abstract"):
            with st.expander("Abstract"):
                st.write(paper["abstract"])

        if paper.get("score") is not None:
            st.progress(min(paper["score"], 1.0), text=f"Relevance: {paper['score']:.2%}")


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard")

    try:
        stats = get_dashboard_stats()
    except Exception as e:
        st.error(f"Could not load dashboard stats. Make sure functions.sql has been executed. Error: {e}")
        st.stop()

    # Top-level metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📄 Papers", stats.get("total_papers", 0))
    c2.metric("👥 Authors", stats.get("total_authors", 0))
    c3.metric("👤 Users", stats.get("total_users", 0))
    c4.metric("🔗 Citations", stats.get("total_citations", 0))
    c5.metric("📊 Avg Citations", stats.get("avg_citations_per_paper", 0))

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🏆 Top Cited Papers")
        top_papers = get_top_cited_papers(5)
        for i, tp in enumerate(top_papers, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {tp['title']}**")
                st.caption(f"👥 {tp['authors']} · 📊 {tp['citation_count']} citations")

    with col_right:
        st.subheader("📊 Papers by Domain")
        domains = get_domain_stats()
        if domains:
            import pandas as pd
            df = pd.DataFrame(domains)
            st.bar_chart(df.set_index("domain")["paper_count"])

    st.markdown("---")
    st.subheader(f"👤 Your Activity")
    activity = get_user_activity_summary(current_user_id)
    ac1, ac2, ac3, ac4 = st.columns(4)
    ac1.metric("🔖 Bookmarks", activity.get("bookmark_count", 0))
    ac2.metric("📋 Want to Read", activity.get("want_to_read", 0))
    ac3.metric("📖 Reading", activity.get("reading", 0))
    ac4.metric("✅ Completed", activity.get("completed", 0))


# ============================================================================
# PAGE: SEARCH PAPERS
# ============================================================================
elif page == "🔍 Search Papers":
    st.title("🔍 Search Papers")

    search_mode = st.radio("Search mode", ["Keyword Search", "Semantic Search (AI)"], horizontal=True)

    if search_mode == "Keyword Search":
        st.subheader("Filter by keywords")
        fc1, fc2 = st.columns(2)
        with fc1:
            title_q = st.text_input("Title contains")
            author_q = st.text_input("Author name contains")
        with fc2:
            year_q = st.text_input("Publication year (exact)")
            domain_q = st.text_input("Domain contains")
        keyword_q = st.text_input("Keyword in title or abstract")

        if st.button("🔍 Search", type="primary"):
            filters = {}
            if title_q.strip():
                filters["title"] = title_q
            if author_q.strip():
                filters["author"] = author_q
            if year_q.strip():
                try:
                    filters["publication_year"] = int(year_q)
                except ValueError:
                    st.warning("Year must be a number")
            if domain_q.strip():
                filters["domain"] = domain_q
            if keyword_q.strip():
                filters["keyword"] = keyword_q

            results = search_papers(filters)
            st.info(f"Found {len(results)} papers")
            for p in results:
                paper_card(p)
        else:
            st.caption("Enter filters above and click Search, or leave all empty to see all papers.")

    else:  # Semantic Search
        if not AI_AVAILABLE:
            st.warning("⚠️ AI module not available. Install `sentence-transformers` and `chromadb` first.")
        else:
            query = st.text_input("Describe what you're looking for",
                                  placeholder="e.g., Research papers about radar signal denoising using deep learning")
            top_k = st.slider("Number of results", 1, 20, 5)

            if st.button("🧠 Semantic Search", type="primary") and query:
                with st.spinner("Searching with AI..."):
                    try:
                        ai_results = ai_semantic_search(query, top_k=top_k)
                        if ai_results:
                            paper_ids = [r["paper_id"] for r in ai_results]
                            scores = {r["paper_id"]: r["score"] for r in ai_results}
                            papers = get_papers_by_ids(paper_ids)
                            st.success(f"Found {len(papers)} relevant papers")
                            for p in papers:
                                p["score"] = scores.get(p["paper_id"], 0)
                                paper_card(p)
                        else:
                            st.info("No results found. Try indexing some papers first.")
                    except Exception as e:
                        st.error(f"Semantic search error: {e}")


# ============================================================================
# PAGE: ADD PAPER
# ============================================================================
elif page == "➕ Add Paper":
    st.title("➕ Add New Paper")

    # Optional PDF Uploader
    uploaded_pdf = st.file_uploader("📄 Upload Research Paper PDF (optional)", type=["pdf"])
    extracted_text = ""
    saved_pdf_rel_path = None

    if uploaded_pdf is not None:
        st.info(f"Uploaded: **{uploaded_pdf.name}** ({uploaded_pdf.size / 1024:.1f} KB)")
        try:
            # Save uploaded PDF to data/papers/
            papers_dir = PROJECT_ROOT / "data" / "papers"
            papers_dir.mkdir(parents=True, exist_ok=True)
            saved_file_path = papers_dir / uploaded_pdf.name
            with open(saved_file_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            saved_pdf_rel_path = f"data/papers/{uploaded_pdf.name}"

            if AI_AVAILABLE:
                extracted_text = extract_text_from_pdf(saved_file_path)
                if extracted_text:
                    st.success(f"Extracted {len(extracted_text)} characters of text from PDF!")
        except Exception as e:
            st.warning(f"Could not save or parse PDF: {e}")

    with st.form("add_paper_form"):
        title = st.text_input("Paper Title *", placeholder="e.g., Attention Is All You Need")
        default_abstract = extracted_text[:1200].strip() if extracted_text else ""
        abstract = st.text_area("Abstract", value=default_abstract, placeholder="Brief summary of the paper...")
        ac1, ac2 = st.columns(2)
        with ac1:
            year = st.number_input("Publication Year", min_value=1900, max_value=2100, value=2025)
        with ac2:
            domain = st.text_input("Domain", placeholder="e.g., Machine Learning, NLP, Signal Processing")
        authors_str = st.text_input("Authors (comma-separated)", placeholder="e.g., John Doe, Jane Smith")
        pdf_path = st.text_input("PDF Path (optional)", value=saved_pdf_rel_path or "", placeholder="data/papers/my_paper.pdf")

        submitted = st.form_submit_button("➕ Add Paper", type="primary")

    if submitted:
        if not title.strip():
            st.error("Title is required!")
        else:
            paper_data = {
                "title": title.strip(),
                "abstract": abstract.strip() or None,
                "publication_year": year,
                "domain": domain.strip() or None,
                "pdf_path": pdf_path.strip() or None,
                "authors": [a.strip() for a in authors_str.split(",") if a.strip()] if authors_str.strip() else [],
            }
            try:
                paper_id = add_paper(paper_data)
                st.success(f"✅ Paper added with ID: {paper_id}")

                # Also index in ChromaDB if AI module is available
                if AI_AVAILABLE and (paper_data["abstract"] or paper_data["title"]):
                    try:
                        ai_index_paper(paper_id, paper_data["title"], paper_data.get("abstract") or "")
                        st.info("🧠 Paper also indexed in ChromaDB for semantic search.")
                    except Exception as e:
                        st.warning(f"Paper saved in database but AI indexing failed: {e}")
            except Exception as e:
                st.error(f"Error adding paper: {e}")


# ============================================================================
# PAGE: PAPER DETAILS
# ============================================================================
elif page == "📄 Paper Details":
    st.title("📄 Paper Details")

    # Check if we came from a "View" button
    default_id = st.session_state.get("view_paper_id", 1)
    paper_id = st.number_input("Enter Paper ID", min_value=1, value=default_id, step=1)

    paper = get_paper(paper_id)
    if not paper:
        st.warning(f"Paper with ID {paper_id} not found.")
    else:
        st.header(paper["title"])
        if paper.get("authors"):
            st.subheader(f"👥 {', '.join(paper['authors'])}")

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("📅 Year", paper.get("publication_year") or "N/A")
        mc2.metric("🏷️ Domain", paper.get("domain") or "N/A")
        mc3.metric("📊 Citations", paper.get("citation_count", 0))

        if paper.get("abstract"):
            st.markdown("### Abstract")
            st.write(paper["abstract"])

        st.markdown("---")

        # Bookmark & Reading Status actions
        act1, act2 = st.columns(2)
        with act1:
            st.markdown("#### 🔖 Bookmark")
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button("Add Bookmark"):
                    if add_bookmark(current_user_id, paper_id):
                        st.success("Bookmarked!")
                    else:
                        st.info("Already bookmarked.")
            with bc2:
                if st.button("Remove Bookmark"):
                    if remove_bookmark(current_user_id, paper_id):
                        st.success("Bookmark removed.")
                    else:
                        st.info("No bookmark to remove.")

        with act2:
            st.markdown("#### 📖 Reading Status")
            new_status = st.selectbox("Set status", ["want_to_read", "reading", "completed"])
            if st.button("Update Status"):
                set_reading_status(current_user_id, paper_id, new_status)
                st.success(f"Status set to '{new_status}'")

        st.markdown("---")

        # Citations section
        ct1, ct2 = st.columns(2)
        with ct1:
            st.markdown("#### 📚 This Paper Cites (References)")
            cited = get_cited_papers(paper_id)
            if cited:
                for c in cited:
                    st.markdown(f"- **[{c['paper_id']}]** {c['title']} ({c.get('publication_year', 'N/A')})")
            else:
                st.caption("No references recorded.")

        with ct2:
            st.markdown("#### 📖 Cited By (Other Papers)")
            citing = get_citing_papers(paper_id)
            if citing:
                for c in citing:
                    st.markdown(f"- **[{c['paper_id']}]** {c['title']} ({c.get('publication_year', 'N/A')})")
            else:
                st.caption("No papers cite this one yet.")

        # Similar Papers (AI)
        if AI_AVAILABLE:
            st.markdown("---")
            st.markdown("#### 🧠 Similar Papers (AI Recommendation)")
            if st.button("Find Similar Papers"):
                with st.spinner("Computing similarity..."):
                    try:
                        similar = ai_get_similar_papers(paper_id, top_k=5)
                        if similar:
                            sim_ids = [s["paper_id"] for s in similar]
                            sim_scores = {s["paper_id"]: s["score"] for s in similar}
                            sim_papers = get_papers_by_ids(sim_ids)
                            for sp in sim_papers:
                                sp["score"] = sim_scores.get(sp["paper_id"], 0)
                                paper_card(sp, show_actions=False)
                        else:
                            st.info("No similar papers found. Make sure papers are indexed.")
                    except Exception as e:
                        st.warning(f"Could not find similar papers: {e}")

        # Danger zone / Paper deletion
        st.markdown("---")
        with st.expander("⚙️ Manage / Delete Paper"):
            st.warning("⚠️ Deleting this paper will also cascade-delete its authors mapping, citations, bookmarks, and AI vector embedding.")
            if st.button("🗑️ Delete Paper", type="secondary"):
                if delete_paper(paper_id):
                    if AI_AVAILABLE:
                        try:
                            ai_delete_paper_embedding(paper_id)
                        except Exception:
                            pass
                    st.success(f"Paper {paper_id} deleted successfully.")
                else:
                    st.error("Failed to delete paper.")


# ============================================================================
# PAGE: MY BOOKMARKS
# ============================================================================
elif page == "📑 My Bookmarks":
    st.title("📑 My Bookmarks")

    bookmarks = get_user_bookmarks(current_user_id)
    if bookmarks:
        st.info(f"You have {len(bookmarks)} bookmarked papers.")
        for p in bookmarks:
            paper_card(p)
    else:
        st.info("No bookmarks yet. Go to a paper's detail page and click 'Add Bookmark'.")


# ============================================================================
# PAGE: READING LIST
# ============================================================================
elif page == "📖 Reading List":
    st.title("📖 Reading List")

    status_filter = st.selectbox("Filter by status", [None, "want_to_read", "reading", "completed"],
                                  format_func=lambda x: "All" if x is None else x.replace("_", " ").title())

    reading = get_user_reading_list(current_user_id, status=status_filter)
    if reading:
        st.info(f"Showing {len(reading)} papers.")
        for p in reading:
            with st.container(border=True):
                badge_map = {"want_to_read": "📋", "reading": "📖", "completed": "✅"}
                badge = badge_map.get(p.get("reading_status"), "")
                st.markdown(f"{badge} **{p.get('reading_status', '').replace('_', ' ').title()}**")
                paper_card(p, show_actions=True)
    else:
        st.info("No papers in your reading list yet.")


# ============================================================================
# PAGE: CITATIONS EXPLORER
# ============================================================================
elif page == "🔗 Citations Explorer":
    st.title("🔗 Citations Explorer")

    st.subheader("Add a Citation")
    with st.form("add_citation_form"):
        cc1, cc2 = st.columns(2)
        with cc1:
            citing_id = st.number_input("Citing Paper ID (the one that cites)", min_value=1, value=1, step=1)
        with cc2:
            cited_id = st.number_input("Cited Paper ID (the one being cited)", min_value=1, value=2, step=1)
        cite_submitted = st.form_submit_button("🔗 Add Citation")

    if cite_submitted:
        if citing_id == cited_id:
            st.error("A paper cannot cite itself!")
        else:
            if add_citation(citing_id, cited_id):
                st.success(f"Citation added: Paper {citing_id} → Paper {cited_id}")
            else:
                st.warning("Citation already exists or invalid paper IDs.")

    st.markdown("---")
    st.subheader("Explore Citations")
    explore_id = st.number_input("Enter Paper ID to explore", min_value=1, value=1, step=1, key="explore")

    paper = get_paper(explore_id)
    if paper:
        st.markdown(f"### {paper['title']}")
        st.caption(f"📊 Citation Count: {paper.get('citation_count', 0)}")

        ex1, ex2 = st.columns(2)
        with ex1:
            st.markdown("#### 📚 References (papers this cites)")
            cited = get_cited_papers(explore_id)
            if cited:
                for c in cited:
                    st.markdown(f"- **[{c['paper_id']}]** {c['title']}")
            else:
                st.caption("None recorded.")
        with ex2:
            st.markdown("#### 📖 Cited By (papers that cite this)")
            citing = get_citing_papers(explore_id)
            if citing:
                for c in citing:
                    st.markdown(f"- **[{c['paper_id']}]** {c['title']}")
            else:
                st.caption("None yet.")
    else:
        st.warning(f"Paper {explore_id} not found.")

