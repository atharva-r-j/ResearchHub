"""
ResearchHub – Modern Streamlit Frontend
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
import pandas as pd

# --- Database imports ---
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

# --- AI imports ---
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
    page_title="ResearchHub · AI Research Suite",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CUSTOM CSS DESIGN SYSTEM
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Background & Spacing */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px;
}

/* ============================================================================
   SIDEBAR POLISHED DESIGN SYSTEM
============================================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090D16 0%, #0D1424 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}

/* Brand Card in Sidebar */
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(139, 92, 246, 0.12) 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 14px;
    margin-bottom: 22px;
    box-shadow: 0 4px 20px -2px rgba(99, 102, 241, 0.2);
}
.brand-icon-wrapper {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.5);
}
.brand-title {
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    background: linear-gradient(135deg, #FFFFFF 0%, #C7D2FE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.brand-subtitle {
    font-size: 0.74rem;
    color: #94A3B8;
    margin: 2px 0 0 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.brand-badge {
    background: rgba(99, 102, 241, 0.3);
    color: #A5B4FC;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    letter-spacing: 0.05em;
}

/* Sidebar Section Headers */
.sidebar-section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    margin: 16px 0 8px 4px;
}

/* Modern Tab Navigation (Transforming Radio Buttons) */
div[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 0 !important;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
    border-radius: 10px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.07) !important;
    transform: translateX(4px) !important;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.22) 0%, rgba(99, 102, 241, 0.05) 100%) !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-left: 3.5px solid #6366F1 !important;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    margin: 0 !important;
    letter-spacing: -0.01em;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p,
div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #F8FAFC !important;
    font-weight: 700 !important;
}

/* AI Engine Sidebar Card */
.ai-engine-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.ai-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.ai-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #F1F5F9;
}
.ai-status-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #34D399;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 2px 7px;
    border-radius: 12px;
}
.ai-card-meta {
    font-size: 0.73rem;
    color: #94A3B8;
    line-height: 1.5;
}
.pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 6px #10B981;
}

/* User Profile Badge */
.user-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    margin-top: 8px;
}
.user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    color: white;
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
}

/* Sidebar Footer */
.sidebar-footer {
    text-align: center;
    margin-top: 24px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 0.72rem;
    color: #64748B;
    line-height: 1.6;
}

/* Metric / KPI Cards */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.25);
    transition: all 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 8px 24px -2px rgba(99, 102, 241, 0.2);
}
div[data-testid="stMetricLabel"] {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
div[data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #F8FAFC !important;
    letter-spacing: -0.02em;
}

/* Custom Paper Card Container */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    margin-bottom: 14px !important;
    transition: all 0.2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 6px 22px -3px rgba(0, 0, 0, 0.3);
}

/* Pill Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    margin-right: 6px;
}
.badge-domain {
    background: rgba(99, 102, 241, 0.15);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.3);
}
.badge-year {
    background: rgba(148, 163, 184, 0.12);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 0.25);
}
.badge-cite {
    background: rgba(245, 158, 11, 0.15);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.35);
}
.badge-relevance {
    background: rgba(16, 185, 129, 0.15);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Section Header Typography */
.hero-header {
    margin-bottom: 22px;
}
.hero-title {
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #F8FAFC;
    margin-bottom: 4px;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #94A3B8;
    margin: 0;
}

/* Button Refinements */
button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
}
button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 500 !important;
}

/* Expander styling */
div[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    background: rgba(15, 23, 42, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR – BRANDING & NAVIGATION
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon-wrapper">📚</div>
        <div>
            <div class="brand-title">ResearchHub</div>
            <div class="brand-subtitle"><span class="brand-badge">PRO</span> AI Discovery Suite</div>
        </div>
    </div>
    <div class="sidebar-section-label">MAIN NAVIGATION</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🔍 Search Papers",
            "➕ Add Paper",
            "📄 Paper Details",
            "📑 My Bookmarks",
            "📖 Reading List",
            "🔗 Citations Explorer",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<div class='sidebar-section-label'>AI & VECTOR ENGINE</div>", unsafe_allow_html=True)

    # AI Status & Sync
    if AI_AVAILABLE:
        st.markdown("""
        <div class="ai-engine-card">
            <div class="ai-card-header">
                <div class="ai-card-title">ChromaDB Store</div>
                <span class="ai-status-tag"><span class="pulse-dot"></span> CONNECTED</span>
            </div>
            <div class="ai-card-meta">
                <div>• Embedding: <b>all-MiniLM-L6</b> (384-d)</div>
                <div>• Distance: <b>Cosine Metric</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Sync All to ChromaDB", use_container_width=True):
            with st.status("Vectorizing all papers into ChromaDB...", expanded=True) as status:
                all_papers = get_all_papers()
                count = ai_index_papers_batch(all_papers)
                status.update(label=f"Successfully indexed {count} papers!", state="complete", expanded=False)
            st.toast(f"✅ Vector database synchronized with {count} papers!", icon="🧠")
    else:
        st.warning("⚠️ AI module inactive. Install `sentence-transformers` and `chromadb` for semantic search.")

    st.markdown("<div class='sidebar-section-label'>ACTIVE RESEARCHER</div>", unsafe_allow_html=True)

    users_map = {
        1: ("Atharva Jadhav", "Lead Researcher", "AJ"),
        2: ("Riya Sharma", "Graduate Scholar", "RS"),
        3: ("Dr. Rajesh Mehta", "Principal Investigator", "RM"),
    }

    current_user_id = st.selectbox(
        "Select User",
        options=[1, 2, 3],
        format_func=lambda uid: users_map.get(uid, (f"User {uid}", "", "U"))[0],
        label_visibility="collapsed",
    )

    uname, urole, uinitials = users_map.get(current_user_id, (f"User {current_user_id}", "Member", "U"))
    st.markdown(f"""
    <div class="user-card">
        <div class="user-avatar">{uinitials}</div>
        <div>
            <div style="font-weight: 700; font-size: 0.88rem; color: #F1F5F9;">{uname}</div>
            <div style="font-size: 0.74rem; color: #94A3B8;">{urole}</div>
        </div>
    </div>

    <div class="sidebar-footer">
        <div>ResearchHub v1.0 · DBMS Lab</div>
        <div style="font-size: 0.68rem; color: #475569;">PostgreSQL · ChromaDB · Streamlit</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# HELPER: Render Styled Paper Card
# ============================================================================
def paper_card(paper, show_actions=True):
    """Render a paper as an elegant card with badges, authors, and quick actions."""
    with st.container(border=True):
        col_main, col_btn = st.columns([5, 1])

        with col_main:
            # Paper Title
            st.markdown(f"### {paper['title']}")

            # Authors List
            authors = paper.get("authors", [])
            if authors:
                authors_str = ", ".join(authors) if isinstance(authors, list) else authors
                st.markdown(f"<span style='color: #94A3B8; font-size: 0.88rem;'>👥 {authors_str}</span>", unsafe_allow_html=True)

            # Metadata Badges
            badges_html = '<div style="margin-top: 8px; margin-bottom: 6px;">'
            if paper.get("domain"):
                badges_html += f'<span class="badge badge-domain">🏷️ {paper["domain"]}</span>'
            if paper.get("publication_year"):
                badges_html += f'<span class="badge badge-year">📅 {paper["publication_year"]}</span>'
            if paper.get("citation_count") is not None:
                badges_html += f'<span class="badge badge-cite">⭐ {paper["citation_count"]} citations</span>'
            if paper.get("score") is not None:
                badges_html += f'<span class="badge badge-relevance">🎯 {paper["score"]:.1%} Match</span>'
            badges_html += '</div>'
            st.markdown(badges_html, unsafe_allow_html=True)

        with col_btn:
            if show_actions:
                pid = paper["paper_id"]
                if st.button("Details →", key=f"btn_view_{pid}", use_container_width=True):
                    st.session_state["view_paper_id"] = pid
                    st.rerun()

        # Collapsible Abstract
        if paper.get("abstract"):
            with st.expander("📄 View Abstract"):
                st.markdown(f"<div style='color: #CBD5E1; font-size: 0.92rem; line-height: 1.6;'>{paper['abstract']}</div>", unsafe_allow_html=True)

        # Relevance Score Bar
        if paper.get("score") is not None:
            st.progress(min(float(paper["score"]), 1.0), text=f"Semantic Relevance: {paper['score']:.1%}")


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Repository Intelligence Dashboard</h1>
        <p class="hero-subtitle">Real-time metrics, citation leaders, and distribution analytics.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        stats = get_dashboard_stats()
    except Exception as e:
        st.error(f"Could not load dashboard stats. Ensure functions.sql is executed. Error: {e}")
        st.stop()

    # Top-level KPI Metrics
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Papers", stats.get("total_papers", 0), help="Registered publications in database")
    k2.metric("Authors", stats.get("total_authors", 0), help="Unique contributors across papers")
    k3.metric("Users", stats.get("total_users", 0), help="Active platform researchers")
    k4.metric("Citations", stats.get("total_citations", 0), help="Total recorded citation links")
    k5.metric("Avg Citations", f"{stats.get('avg_citations_per_paper', 0):.1f}", help="Average citations per paper")

    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🏆 Most Cited Papers")
        top_papers = get_top_cited_papers(5)
        for i, tp in enumerate(top_papers, 1):
            with st.container(border=True):
                col_rank, col_info = st.columns([1, 10])
                with col_rank:
                    st.markdown(f"<div style='font-size: 1.25rem; font-weight: 800; color: #818CF8;'>#{i}</div>", unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"**{tp['title']}**")
                    st.markdown(f"<span style='color: #94A3B8; font-size: 0.8rem;'>👥 {tp['authors']}</span> · <span class='badge badge-cite'>⭐ {tp['citation_count']} citations</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown("#### 📊 Domain Distribution")
        domains = get_domain_stats()
        if domains:
            df = pd.DataFrame(domains)
            st.bar_chart(df.set_index("domain")["paper_count"], color="#6366F1")

    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    st.markdown(f"#### 👤 Personal Progress ({uname})")
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
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Search & Discovery Engine</h1>
        <p class="hero-subtitle">Find literature using relational SQL filtering or AI semantic vector similarity.</p>
    </div>
    """, unsafe_allow_html=True)

    search_mode = st.radio(
        "Search Mode",
        ["🔍 Keyword & Relational Filters", "🧠 Semantic Search (AI Powered)"],
        horizontal=True,
    )

    if search_mode == "🔍 Keyword & Relational Filters":
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                title_q = st.text_input("Title Contains", placeholder="e.g. Residual, Attention, Radar")
                author_q = st.text_input("Author Name Contains", placeholder="e.g. Hinton, Vaswani, He")
            with fc2:
                year_q = st.text_input("Publication Year (exact)", placeholder="e.g. 2023")
                domain_q = st.text_input("Domain Contains", placeholder="e.g. Computer Vision, NLP")
            keyword_q = st.text_input("Broad Keyword (searches Title + Abstract)", placeholder="e.g. adversarial, denoising, transformer")

            btn_search = st.button("🔍 Search Publications", type="primary", use_container_width=True)

        if btn_search:
            filters = {}
            if title_q.strip():
                filters["title"] = title_q.strip()
            if author_q.strip():
                filters["author"] = author_q.strip()
            if year_q.strip():
                try:
                    filters["publication_year"] = int(year_q.strip())
                except ValueError:
                    st.warning("Publication year must be an integer.")
            if domain_q.strip():
                filters["domain"] = domain_q.strip()
            if keyword_q.strip():
                filters["keyword"] = keyword_q.strip()

            results = search_papers(filters)
            st.markdown(f"#### Results ({len(results)} matches)")
            for p in results:
                paper_card(p)
        else:
            st.caption("Apply filters and click Search, or click Search with empty fields to view all cataloged papers.")

    else:  # Semantic Search
        if not AI_AVAILABLE:
            st.warning("⚠️ AI module is not loaded. Install requirements to enable semantic search.")
        else:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                query = st.text_input(
                    "Describe your research topic or query in plain natural language:",
                    placeholder="e.g. radar signal denoising using convolutional autoencoders or residual neural networks",
                )
                top_k = st.slider("Top results to retrieve", min_value=1, max_value=20, value=5)
                btn_sem = st.button("🧠 Run Semantic Search", type="primary", use_container_width=True)

            if btn_sem and query:
                with st.spinner("Embedding query & searching vector space..."):
                    try:
                        ai_results = ai_semantic_search(query, top_k=top_k)
                        if ai_results:
                            paper_ids = [r["paper_id"] for r in ai_results]
                            scores = {r["paper_id"]: r["score"] for r in ai_results}
                            papers = get_papers_by_ids(paper_ids)
                            st.markdown(f"#### Top {len(papers)} Semantically Relevant Papers")
                            for p in papers:
                                p["score"] = scores.get(p["paper_id"], 0)
                                paper_card(p)
                        else:
                            st.info("No matching papers found. Try clicking 'Sync All to ChromaDB' in the sidebar first.")
                    except Exception as e:
                        st.error(f"Semantic search error: {e}")


# ============================================================================
# PAGE: ADD PAPER
# ============================================================================
elif page == "➕ Add Paper":
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Ingest Research Paper</h1>
        <p class="hero-subtitle">Upload a PDF document with auto-text extraction, or enter paper metadata manually.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        uploaded_pdf = st.file_uploader("📄 Upload Research Paper PDF (optional)", type=["pdf"])
        extracted_text = ""
        saved_pdf_rel_path = None

        if uploaded_pdf is not None:
            st.success(f"Uploaded: **{uploaded_pdf.name}** ({uploaded_pdf.size / 1024:.1f} KB)")
            try:
                papers_dir = PROJECT_ROOT / "data" / "papers"
                papers_dir.mkdir(parents=True, exist_ok=True)
                saved_file_path = papers_dir / uploaded_pdf.name
                with open(saved_file_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())
                saved_pdf_rel_path = f"data/papers/{uploaded_pdf.name}"

                if AI_AVAILABLE:
                    extracted_text = extract_text_from_pdf(saved_file_path)
                    if extracted_text:
                        st.info(f"✨ PyMuPDF extracted {len(extracted_text)} characters from the document.")
            except Exception as e:
                st.warning(f"Could not parse PDF: {e}")

    with st.form("add_paper_form"):
        title = st.text_input("Paper Title *", placeholder="e.g. Attention Is All You Need")
        default_abstract = extracted_text[:1200].strip() if extracted_text else ""
        abstract = st.text_area("Abstract", value=default_abstract, placeholder="Enter or verify paper abstract summary...", height=140)
        
        ac1, ac2 = st.columns(2)
        with ac1:
            year = st.number_input("Publication Year", min_value=1900, max_value=2100, value=2024)
        with ac2:
            domain = st.text_input("Domain", placeholder="e.g. Computer Vision, NLP, Signal Processing")
            
        authors_str = st.text_input("Authors (comma-separated)", placeholder="e.g. Ashish Vaswani, Noam Shazeer, Niki Parmar")
        pdf_path = st.text_input("PDF File Path", value=saved_pdf_rel_path or "", placeholder="data/papers/paper.pdf")

        submitted = st.form_submit_button("➕ Save Paper & Generate Embeddings", type="primary", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Paper Title is required.")
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
                st.success(f"🎉 Paper saved to PostgreSQL with ID: **{paper_id}**")

                if AI_AVAILABLE and (paper_data["abstract"] or paper_data["title"]):
                    try:
                        ai_index_paper(paper_id, paper_data["title"], paper_data.get("abstract") or "")
                        st.toast("🧠 Vector embeddings created & saved to ChromaDB!", icon="✅")
                    except Exception as e:
                        st.warning(f"Paper recorded in database, but vector embedding failed: {e}")
            except Exception as e:
                st.error(f"Error adding paper: {e}")


# ============================================================================
# PAGE: PAPER DETAILS
# ============================================================================
elif page == "📄 Paper Details":
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Publication Deep Dive</h1>
        <p class="hero-subtitle">Inspect citation references, bookmark items, and generate AI recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    default_id = st.session_state.get("view_paper_id", 1)
    paper_id = st.number_input("Enter or Select Paper ID", min_value=1, value=default_id, step=1)

    paper = get_paper(paper_id)
    if not paper:
        st.warning(f"Paper with ID {paper_id} not found in database.")
    else:
        # Header banner
        with st.container(border=True):
            st.markdown(f"## {paper['title']}")
            if paper.get("authors"):
                st.markdown(f"<span style='color: #94A3B8; font-size: 1rem;'>👥 {', '.join(paper['authors'])}</span>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Publication Year", paper.get("publication_year") or "N/A")
            mc2.metric("Research Domain", paper.get("domain") or "General")
            mc3.metric("Citation Count", paper.get("citation_count", 0))

            if paper.get("abstract"):
                st.markdown("### Abstract")
                st.markdown(f"<div style='color: #E2E8F0; font-size: 0.95rem; line-height: 1.7;'>{paper['abstract']}</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

        # Action section
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            with st.container(border=True):
                st.markdown("#### 🔖 Bookmarks")
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("Add Bookmark", use_container_width=True):
                        if add_bookmark(current_user_id, paper_id):
                            st.success("Bookmarked!")
                        else:
                            st.info("Already in bookmarks.")
                with bc2:
                    if st.button("Remove Bookmark", use_container_width=True):
                        if remove_bookmark(current_user_id, paper_id):
                            st.success("Removed.")
                        else:
                            st.info("Not bookmarked.")

        with col_act2:
            with st.container(border=True):
                st.markdown("#### 📖 Reading Tracker")
                rc1, rc2 = st.columns([2, 1])
                with rc1:
                    new_status = st.selectbox(
                        "Reading Status",
                        ["want_to_read", "reading", "completed"],
                        format_func=lambda s: s.replace("_", " ").title(),
                        label_visibility="collapsed",
                    )
                with rc2:
                    if st.button("Set Status", use_container_width=True):
                        set_reading_status(current_user_id, paper_id, new_status)
                        st.success(f"Updated!")

        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

        # Citations Graph Explorer
        ct1, ct2 = st.columns(2)
        with ct1:
            with st.container(border=True):
                st.markdown("#### 📚 References (Papers this cites)")
                cited = get_cited_papers(paper_id)
                if cited:
                    for c in cited:
                        st.markdown(f"- **[{c['paper_id']}]** {c['title']} *({c.get('publication_year', 'N/A')})*")
                else:
                    st.caption("No references recorded in citation graph.")

        with ct2:
            with st.container(border=True):
                st.markdown("#### 📖 Cited By (Papers citing this)")
                citing = get_citing_papers(paper_id)
                if citing:
                    for c in citing:
                        st.markdown(f"- **[{c['paper_id']}]** {c['title']} *({c.get('publication_year', 'N/A')})*")
                else:
                    st.caption("No papers currently cite this publication.")

        # AI Recommendation Section
        if AI_AVAILABLE:
            st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
            st.markdown("### 🧠 AI Similar Papers Recommendation")
            st.caption("Discovers topologically nearest papers in the 384-dimensional latent embedding space.")
            if st.button("Find Similar Papers", type="primary"):
                with st.spinner("Finding nearest neighbors in ChromaDB..."):
                    try:
                        similar = ai_get_similar_papers(paper_id, top_k=5)
                        if similar:
                            sim_ids = [s["paper_id"] for s in similar]
                            sim_scores = {s["paper_id"]: s["score"] for s in similar}
                            sim_papers = get_papers_by_ids(sim_ids)
                            for sp in sim_papers:
                                sp["score"] = sim_scores.get(sp["paper_id"], 0)
                                paper_card(sp, show_actions=True)
                        else:
                            st.info("No similar papers found. Verify that the repository is synced.")
                    except Exception as e:
                        st.warning(f"Could not compute recommendations: {e}")

        # Danger zone / Deletion
        st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
        with st.expander("⚙️ Manage Publication / Delete Paper"):
            st.warning("⚠️ Deleting will permanently remove this record from PostgreSQL, along with author links, citations, bookmarks, and ChromaDB vector embeddings.")
            if st.button("🗑️ Permanently Delete Paper", type="secondary"):
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
    st.markdown(f"""
    <div class="hero-header">
        <h1 class="hero-title">Saved Bookmarks</h1>
        <p class="hero-subtitle">Publications saved for reference by {uname}.</p>
    </div>
    """, unsafe_allow_html=True)

    bookmarks = get_user_bookmarks(current_user_id)
    if bookmarks:
        st.markdown(f"#### Saved Publications ({len(bookmarks)})")
        for p in bookmarks:
            paper_card(p)
    else:
        st.info("No bookmarks saved yet. Explore papers and click 'Add Bookmark' on their details page.")


# ============================================================================
# PAGE: READING LIST
# ============================================================================
elif page == "📖 Reading List":
    st.markdown(f"""
    <div class="hero-header">
        <h1 class="hero-title">Personal Reading Pipeline</h1>
        <p class="hero-subtitle">Track reading progress and milestones for {uname}.</p>
    </div>
    """, unsafe_allow_html=True)

    status_filter = st.selectbox(
        "Filter by reading state",
        [None, "want_to_read", "reading", "completed"],
        format_func=lambda x: "All States" if x is None else x.replace("_", " ").title(),
    )

    reading = get_user_reading_list(current_user_id, status=status_filter)
    if reading:
        st.markdown(f"#### Tracked Papers ({len(reading)})")
        for p in reading:
            badge_map = {"want_to_read": "📋 Want to Read", "reading": "📖 Reading", "completed": "✅ Completed"}
            state_text = badge_map.get(p.get("reading_status"), "Status")
            st.markdown(f"<span class='badge badge-domain'>{state_text}</span>", unsafe_allow_html=True)
            paper_card(p, show_actions=True)
    else:
        st.info("No publications currently in this reading category.")


# ============================================================================
# PAGE: CITATIONS EXPLORER
# ============================================================================
elif page == "🔗 Citations Explorer":
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Citation Graph Explorer</h1>
        <p class="hero-subtitle">Map relationships, link publications, and navigate citation networks.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 🔗 Record a New Citation Link")
        with st.form("add_citation_form"):
            cc1, cc2 = st.columns(2)
            with cc1:
                citing_id = st.number_input("Citing Paper ID (source)", min_value=1, value=1, step=1)
            with cc2:
                cited_id = st.number_input("Cited Paper ID (target reference)", min_value=1, value=2, step=1)
            cite_submitted = st.form_submit_button("Create Citation Edge", type="primary", use_container_width=True)

        if cite_submitted:
            if citing_id == cited_id:
                st.error("A paper cannot cite itself (self-citation constraint).")
            else:
                if add_citation(citing_id, cited_id):
                    st.success(f"✅ Citation edge established: Paper {citing_id} ➔ Paper {cited_id} (Citation count auto-incremented by trigger)")
                else:
                    st.warning("Citation edge already exists or one of the paper IDs is invalid.")

    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 🔍 Inspect Citation Network")
        explore_id = st.number_input("Target Paper ID", min_value=1, value=1, step=1, key="explore_cite")

        paper = get_paper(explore_id)
        if paper:
            st.markdown(f"### {paper['title']}")
            st.markdown(f"<span class='badge badge-cite'>⭐ {paper.get('citation_count', 0)} Total Inbound Citations</span>", unsafe_allow_html=True)

            ex1, ex2 = st.columns(2)
            with ex1:
                st.markdown("##### 📚 References Outbound (This paper cites)")
                cited = get_cited_papers(explore_id)
                if cited:
                    for c in cited:
                        st.markdown(f"- **[{c['paper_id']}]** {c['title']} *({c.get('publication_year', 'N/A')})*")
                else:
                    st.caption("No outbound references recorded.")

            with ex2:
                st.markdown("##### 📖 Inbound Citations (Cited by others)")
                citing = get_citing_papers(explore_id)
                if citing:
                    for c in citing:
                        st.markdown(f"- **[{c['paper_id']}]** {c['title']} *({c.get('publication_year', 'N/A')})*")
                else:
                    st.caption("No inbound citations recorded yet.")
        else:
            st.warning(f"Paper ID {explore_id} not found.")
