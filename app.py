"""Streamlit Web Application: AI Document Comparison Assistant.

Provides an executive-grade web interface for uploading two PDF documents,
inspecting extracted text, executing evidence-grounded comparisons with
Google Gemini, reviewing structured differences, and downloading DOCX reports.
"""

from datetime import datetime
import io
import os
import streamlit as st

from config import (
    APP_DISCLAIMER,
    APP_SUBTITLE,
    APP_TITLE,
    AVAILABLE_MODELS,
    DEFAULT_GEMINI_MODEL,
    MAX_CHARS_PER_DOC,
    MAX_FILE_SIZE_MB,
    MAX_PAGES_PER_DOC,
    MAX_TOTAL_CHARS,
    get_gemini_api_key,
)
from comparison import DocumentComparator
from document_reader import extract_text_from_pdf, validate_document_pair
from report_generator import generate_docx_report
from schemas import ComparisonResult, DocumentInfo

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- MODERN CUSTOM CSS STYLING ---
st.markdown(
    """
    <style>
    /* Main container and typography */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Global Card Style */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    /* Header Container */
    .app-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .app-header h1 {
        color: #F8FAFC !important;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .app-header p {
        color: #94A3B8 !important;
        font-size: 14px;
        margin-bottom: 0px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-added { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
    .badge-removed { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
    .badge-modified { background-color: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; }
    .badge-contradiction { background-color: #F3E8FF; color: #7E22CE; border: 1px solid #D8B4FE; }
    .badge-wording { background-color: #E0F2FE; color: #0369A1; border: 1px solid #BAE6FD; }
    .badge-same { background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; }
    
    /* Detail comparison card */
    .detail-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
    }
    
    /* Citation quote */
    .citation-box {
        background-color: #F8FAFC;
        border-left: 3px solid #3B82F6;
        padding: 8px 12px;
        font-size: 12px;
        color: #475569;
        margin-top: 6px;
        border-radius: 0 4px 4px 0;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SESSION STATE INITIALIZATION ---
if "doc_a_info" not in st.session_state:
    st.session_state.doc_a_info = None
if "doc_b_info" not in st.session_state:
    st.session_state.doc_b_info = None
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "sample_loaded" not in st.session_state:
    st.session_state.sample_loaded = False


def reset_application_state():
    """Resets all uploaded files and comparison state."""
    st.session_state.doc_a_info = None
    st.session_state.doc_b_info = None
    st.session_state.comparison_result = None
    st.session_state.is_processing = False
    st.session_state.sample_loaded = False
    st.rerun()


def load_sample_documents():
    """Loads bundled sample policy documents for quick testing."""
    sample_a_path = os.path.join("sample_documents", "policy_v1.pdf")
    sample_b_path = os.path.join("sample_documents", "policy_v2.pdf")

    if os.path.exists(sample_a_path) and os.path.exists(sample_b_path):
        with open(sample_a_path, "rb") as f_a:
            st.session_state.doc_a_info = extract_text_from_pdf(f_a.read(), "policy_v1.pdf")
        with open(sample_b_path, "rb") as f_b:
            st.session_state.doc_b_info = extract_text_from_pdf(f_b.read(), "policy_v2.pdf")
        st.session_state.comparison_result = None
        st.session_state.sample_loaded = True
        st.rerun()
    else:
        st.sidebar.error("Sample documents could not be found in sample_documents/ directory.")


# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    # Configured Gemini AI Model (Fixed to backend-supported gemini-2.5-flash)
    selected_model = DEFAULT_GEMINI_MODEL
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
            <div style="font-size: 11px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Gemini AI Model</div>
            <div style="font-size: 14px; font-weight: 600; color: #0F172A; display: flex; align-items: center; gap: 6px;">
                <span>🤖</span> <code>{selected_model}</code>
            </div>
            <div style="font-size: 11px; color: #16A34A; margin-top: 4px; font-weight: 500;">
                ● Configured &amp; Active
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # API Key Configuration
    st.markdown("---")
    st.markdown("### 🔑 API Authentication")
    env_key = get_gemini_api_key()
    user_api_key = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        placeholder="Enter AI Studio API Key...",
        help="Your key is kept locally in session and never logged or exposed.",
    )
    
    if not user_api_key:
        st.warning("⚠️ Enter a Gemini API Key or set `GEMINI_API_KEY` in `.env` to execute comparisons.")
    else:
        st.success("✅ API Key configured")

    # Sample Document Quick-Load Button
    st.markdown("---")
    st.markdown("### 🚀 Fast Demo")
    if st.button("📁 Load Sample Documents", use_container_width=True, help="Instantly load Policy v1.2 and Policy v2.0 sample PDFs"):
        load_sample_documents()

    if st.session_state.sample_loaded:
        st.info("ℹ️ Bundled sample documents loaded into Document A and Document B.")

    # Processing Limits Info
    st.markdown("---")
    st.markdown("### 🛡️ Guardrails & Limits")
    st.caption(f"• **Max File Size:** {MAX_FILE_SIZE_MB} MB per file")
    st.caption(f"• **Max Page Count:** {MAX_PAGES_PER_DOC} pages / doc")
    st.caption(f"• **Max Characters:** {MAX_CHARS_PER_DOC:,} / doc")
    st.caption(f"• **Max Combined:** {MAX_TOTAL_CHARS:,} chars")

    # Reset Action
    st.markdown("---")
    if st.button("🔄 Reset / Clear Session", use_container_width=True):
        reset_application_state()

    # Viva & Submitter Info
    st.markdown("---")
    st.caption("**Internship Project:** AI Document Comparison Assistant")
    st.caption("**Organization:** Xpert Champs AI Engineering")
    st.caption("**Technology:** Python, Streamlit, Gemini API, pypdf, python-docx")


# --- APPLICATION HEADER ---
st.markdown(
    f"""
    <div class="app-header">
        <h1>{APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"ℹ️ {APP_DISCLAIMER}")

# --- DOCUMENT UPLOAD & VALIDATION AREA ---
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📄 Document A (Baseline)")
    uploaded_file_a = st.file_uploader(
        "Upload Document A (PDF)",
        type=["pdf"],
        key="uploader_a",
        help="Upload the reference, initial, or older version of the document.",
    )

    if uploaded_file_a is not None:
        st.session_state.doc_a_info = extract_text_from_pdf(uploaded_file_a, uploaded_file_a.name)
        st.session_state.sample_loaded = False

    # Display Document A status
    doc_a = st.session_state.doc_a_info
    if doc_a:
        if doc_a.is_valid:
            st.success(f"**Loaded:** {doc_a.filename}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Pages", doc_a.page_count)
            m2.metric("Characters", f"{doc_a.character_count:,}")
            m3.metric("Words", f"{doc_a.word_count:,}")

            with st.expander("🔍 Inspect Extracted Text Preview"):
                st.text_area(
                    "Extracted Text (Document A)",
                    value=doc_a.full_text[:3000] + ("\n... [Truncated for preview]" if len(doc_a.full_text) > 3000 else ""),
                    height=200,
                    disabled=True,
                )
        else:
            st.error(f"❌ **Validation Failed:** {doc_a.error_message}")
    else:
        st.info("Please upload a PDF document for Document A.")

with col_b:
    st.markdown("### 📄 Document B (Comparison)")
    uploaded_file_b = st.file_uploader(
        "Upload Document B (PDF)",
        type=["pdf"],
        key="uploader_b",
        help="Upload the updated, revised, or alternative version of the document.",
    )

    if uploaded_file_b is not None:
        st.session_state.doc_b_info = extract_text_from_pdf(uploaded_file_b, uploaded_file_b.name)
        st.session_state.sample_loaded = False

    # Display Document B status
    doc_b = st.session_state.doc_b_info
    if doc_b:
        if doc_b.is_valid:
            st.success(f"**Loaded:** {doc_b.filename}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Pages", doc_b.page_count)
            m2.metric("Characters", f"{doc_b.character_count:,}")
            m3.metric("Words", f"{doc_b.word_count:,}")

            with st.expander("🔍 Inspect Extracted Text Preview"):
                st.text_area(
                    "Extracted Text (Document B)",
                    value=doc_b.full_text[:3000] + ("\n... [Truncated for preview]" if len(doc_b.full_text) > 3000 else ""),
                    height=200,
                    disabled=True,
                )
        else:
            st.error(f"❌ **Validation Failed:** {doc_b.error_message}")
    else:
        st.info("Please upload a PDF document for Document B.")

# --- COMPARISON ACTION BUTTON ---
st.markdown("---")

can_compare = (
    doc_a is not None
    and doc_b is not None
    and doc_a.is_valid
    and doc_b.is_valid
)

btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    compare_btn = st.button(
        "🚀 Compare Documents",
        type="primary",
        disabled=not can_compare or st.session_state.is_processing,
        use_container_width=True,
    )

if not can_compare:
    st.caption("ℹ️ Upload and validate both Document A and Document B to enable the comparison engine.")

# --- EXECUTE COMPARISON ---
if compare_btn and can_compare:
    # Validate combined limits
    is_valid_pair, pair_error = validate_document_pair(doc_a, doc_b)
    if not is_valid_pair:
        st.error(f"❌ **Pair Validation Error:** {pair_error}")
    elif not user_api_key:
        st.error("❌ **Missing API Key:** Please enter your Gemini API key in the sidebar to run the comparison.")
    else:
        st.session_state.is_processing = True
        with st.spinner("Analyzing documents with Gemini AI... Evaluating similarities, differences, and key details..."):
            try:
                comparator = DocumentComparator(
                    api_key=user_api_key,
                    model_name=selected_model,
                )
                result = comparator.compare(doc_a, doc_b)
                st.session_state.comparison_result = result
                st.session_state.is_processing = False
                st.success("✅ Comparison completed successfully!")
                st.rerun()
            except Exception as e:
                st.session_state.is_processing = False
                st.error(f"❌ **Comparison Error:** {str(e)}")


# --- DISPLAY COMPARISON RESULTS ---
res: ComparisonResult = st.session_state.comparison_result

if res:
    st.markdown("---")
    st.markdown(f"## 📊 Comparison Analysis: `{res.doc_a_name}` vs `{res.doc_b_name}`")
    st.caption(f"Generated at **{res.timestamp}** using model **{res.model_used}**")

    # Download Report Button
    docx_buffer = generate_docx_report(res)
    safe_name_a = os.path.splitext(res.doc_a_name or "DocA")[0]
    safe_name_b = os.path.splitext(res.doc_b_name or "DocB")[0]
    report_filename = f"comparison_report_{safe_name_a}_vs_{safe_name_b}.docx"

    st.download_button(
        label="📥 Download Comparison Report (.docx)",
        data=docx_buffer,
        file_name=report_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=False,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 6 Dedicated Result Tabs
    tab_sum_a, tab_sum_b, tab_sim, tab_diff, tab_details, tab_conc = st.tabs(
        [
            "📑 Summary A",
            "📑 Summary B",
            "🤝 Similarities",
            "🔍 Differences",
            "📋 Key Details",
            "🏁 Conclusion & Limits",
        ]
    )

    # TAB 1: SUMMARY A
    with tab_sum_a:
        st.markdown(f"### Document A Summary (`{res.doc_a_name}`)")
        st.info(res.document_a_summary or "No summary generated.")
        if doc_a:
            st.caption(f"Document Metrics: {doc_a.page_count} Pages | {doc_a.character_count:,} Characters | {doc_a.word_count:,} Words")

    # TAB 2: SUMMARY B
    with tab_sum_b:
        st.markdown(f"### Document B Summary (`{res.doc_b_name}`)")
        st.info(res.document_b_summary or "No summary generated.")
        if doc_b:
            st.caption(f"Document Metrics: {doc_b.page_count} Pages | {doc_b.character_count:,} Characters | {doc_b.word_count:,} Words")

    # TAB 3: SIMILARITIES
    with tab_sim:
        st.markdown("### Core Similarities & Shared Provisions")
        if not res.similarities:
            st.write("No identical provisions or shared clauses were identified.")
        else:
            for idx, sim in enumerate(res.similarities, start=1):
                with st.container():
                    st.markdown(f"#### {idx}. {sim.topic}")
                    st.write(sim.description)

                    ev_col1, ev_col2 = st.columns(2)
                    with ev_col1:
                        if sim.evidence_a:
                            pages_a_str = f" (p. {', '.join(map(str, sim.pages_a))})" if sim.pages_a else ""
                            st.markdown(
                                f"""<div class="citation-box"><strong>Evidence A{pages_a_str}:</strong> "{sim.evidence_a}"</div>""",
                                unsafe_allow_html=True,
                            )
                    with ev_col2:
                        if sim.evidence_b:
                            pages_b_str = f" (p. {', '.join(map(str, sim.pages_b))})" if sim.pages_b else ""
                            st.markdown(
                                f"""<div class="citation-box"><strong>Evidence B{pages_b_str}:</strong> "{sim.evidence_b}"</div>""",
                                unsafe_allow_html=True,
                            )
                    st.markdown("---")

    # TAB 4: DIFFERENCES
    with tab_diff:
        st.markdown("### Meaningful Differences & Modifications")
        if not res.differences:
            st.write("No substantive differences or contradictions were identified.")
        else:
            # Filter bar for change types
            change_types = sorted(list(set(d.change_type for d in res.differences)))
            selected_filter = st.multiselect(
                "Filter by change type:",
                options=change_types,
                default=change_types,
            )

            filtered_diffs = [d for d in res.differences if d.change_type in selected_filter]
            st.caption(f"Showing **{len(filtered_diffs)}** of {len(res.differences)} detected differences.")

            for diff in filtered_diffs:
                badge_class = f"badge-{diff.change_type.lower()}"
                st.markdown(
                    f"""
                    <div class="detail-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #1E293B;">{diff.topic}</h4>
                            <span class="badge {badge_class}">{diff.change_type.upper()}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.markdown(f"**Document A Baseline (`{res.doc_a_name}`):**")
                    st.write(diff.document_a_value or "*(Not specified)*")
                    if diff.evidence_a:
                        pages_a_str = f" (p. {', '.join(map(str, diff.pages_a))})" if diff.pages_a else ""
                        st.markdown(
                            f"""<div class="citation-box"><strong>Cite A{pages_a_str}:</strong> "{diff.evidence_a}"</div>""",
                            unsafe_allow_html=True,
                        )

                with d_col2:
                    st.markdown(f"**Document B Comparison (`{res.doc_b_name}`):**")
                    st.write(diff.document_b_value or "*(Not specified)*")
                    if diff.evidence_b:
                        pages_b_str = f" (p. {', '.join(map(str, diff.pages_b))})" if diff.pages_b else ""
                        st.markdown(
                            f"""<div class="citation-box"><strong>Cite B{pages_b_str}:</strong> "{diff.evidence_b}"</div>""",
                            unsafe_allow_html=True,
                        )

                if diff.impact:
                    st.markdown(f"💡 **Practical Impact:** {diff.impact}")
                st.markdown("---")

    # TAB 5: KEY DETAILS
    with tab_details:
        st.markdown("### Key Details Comparison (Dates, Fees, Deadlines, Criteria)")
        if not res.key_details:
            st.write("No specific factual criteria were matched for side-by-side inspection.")
        else:
            table_data = []
            for kd in res.key_details:
                table_data.append(
                    {
                        "Field": kd.field,
                        f"Doc A ({res.doc_a_name or 'A'})": kd.document_a_value,
                        f"Doc B ({res.doc_b_name or 'B'})": kd.document_b_value,
                        "Status": kd.status.replace("_", " ").upper(),
                    }
                )
            st.dataframe(table_data, use_container_width=True)

            with st.expander("🔍 View Detailed Citations for Key Details"):
                for kd in res.key_details:
                    st.markdown(f"**{kd.field}** — *Status: {kd.status.upper()}*")
                    if kd.evidence_a or kd.evidence_b:
                        c_a, c_b = st.columns(2)
                        with c_a:
                            if kd.evidence_a:
                                pages_a_str = f" (p. {', '.join(map(str, kd.pages_a))})" if kd.pages_a else ""
                                st.caption(f"Evidence A{pages_a_str}: \"{kd.evidence_a}\"")
                        with c_b:
                            if kd.evidence_b:
                                pages_b_str = f" (p. {', '.join(map(str, kd.pages_b))})" if kd.pages_b else ""
                                st.caption(f"Evidence B{pages_b_str}: \"{kd.evidence_b}\"")
                    st.markdown("---")

    # TAB 6: CONCLUSION & LIMITATIONS
    with tab_conc:
        st.markdown("### Overall Conclusion")
        st.info(res.overall_conclusion or "No conclusion generated.")

        st.markdown("### Processing Limitations & Uncertainties")
        if res.limitations:
            for lim in res.limitations:
                st.markdown(f"- {lim}")
        else:
            st.write("No textual ambiguities or processing limitations reported.")

        st.markdown("---")
        st.caption(f"**Legal & Compliance Notice:** {APP_DISCLAIMER}")

