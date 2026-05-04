from sympy import false
import streamlit as st
import sys
import os
import tempfile
import json

# Fix import paths to allow importing from agents, state, etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph import workflow
from app.pdf_export import generate_pdf

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Diagnoverse", page_icon="🧬", layout="wide")

# ── Custom CSS for Premium Dark Glassmorphism ────────────────────────────────
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #0a0e1a;
        color: #f0f2f8;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers & Text */
    h1, h2, h3, h4, p, span {
        color: #f0f2f8 !important;
    }
    
    /* Main Title Gradient */
    .gradient-text {
        background: linear-gradient(90deg, #00d4aa 0%, #8264eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    
    /* Cards (Glassmorphism) */
    .glass-card {
        background: rgba(40, 48, 70, 0.4);
        border: 1px solid rgba(0, 212, 170, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Alert styling */
    .stAlert {
        background: rgba(40, 48, 70, 0.4) !important;
        border: 1px solid rgba(255, 107, 107, 0.4) !important;
        color: #f0f2f8 !important;
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #00d4aa 0%, #00b38f 100%);
        color: #0a0e1a !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.4);
    }
    
    /* Download Button */
    .stDownloadButton>button {
        background: linear-gradient(90deg, #8264eb 0%, #684ac9 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        margin-top: 10px;
    }
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(130, 100, 235, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(40, 48, 70, 0.4);
        border-radius: 8px 8px 0px 0px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: none;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 212, 170, 0.1);
        border-top: 2px solid #00d4aa;
    }
    
    /* Table Styling */
    table {
        width: 100%;
        color: #f0f2f8;
        border-collapse: collapse;
    }
    th {
        background-color: rgba(0, 212, 170, 0.1);
        text-align: left;
        padding: 12px;
        color: #00d4aa !important;
    }
    td {
        padding: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Status pills */
    .status-normal { color: #48c78e; font-weight: 600; }
    .status-high { color: #ff6b6b; font-weight: 600; }
    .status-low { color: #ffa726; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="gradient-text">DIAGNOVERSE</div>', unsafe_allow_html=True)
st.markdown("### AI-Powered Medical Report Intelligence")
st.write("Upload a medical report PDF to extract key findings, analyze lab results, review medication interactions, and generate questions for your doctor.")

st.warning("⚠️ **Disclaimer:** Diagnoverse is an AI-powered experimental tool intended for informational purposes only. It can make mistakes and should not be trusted blindly. This tool is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with your doctor or a qualified healthcare provider regarding any medical conditions.")

st.markdown("---")

# ── Upload Zone ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Upload your medical report (PDF)", type=["pdf"])

if "result" not in st.session_state:
    st.session_state["result"] = None
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None

if uploaded_file:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"File ready: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    with col2:
        analyze_btn = st.button("🚀 Analyze Report", use_container_width=True)

    if analyze_btn:
        with st.status("🧠 Processing Medical Report...", expanded=True) as status:
            st.write("🔍 Extracting text and medical entities...")
            
            try:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_path = tmp.name
                
                # Invoke workflow
                st.write("⚙️ Running Agent Pipeline...")
                result = workflow.invoke({
                    "input_type": "pdf",
                    "input_data": temp_path,
                    "file_name": uploaded_file.name
                })
                
                # We can deduce steps based on output
                if result.get("medications"):
                    st.write("💊 Medications detected. Analyzing side effects and interactions...")
                else:
                    st.write("⏩ No medications found. Skipping drug checks.")
                
                st.write("❓ Generating personalized questions for your doctor...")
                st.write("📋 Summarizing clinical findings...")
                
                st.session_state["result"] = result
                
                # Generate PDF immediately so it's ready
                st.write("📄 Generating downloadable PDF report...")
                pdf_bytes = generate_pdf(result, uploaded_file.name)
                st.session_state["pdf_bytes"] = pdf_bytes
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                
            except Exception as e:
                status.update(label="❌ Error during analysis", state="error", expanded=True)
                st.error(f"An error occurred: {str(e)}")

# ── Results Dashboard ──────────────────────────────────────────────────────────
if st.session_state["result"] is not None:
    st.markdown("---")
    
    # ── Prominent Download Button ──
    if st.session_state["pdf_bytes"] is not None:
        st.download_button(
            label="📥 Download Full PDF Report",
            data=st.session_state["pdf_bytes"],
            file_name=f"Diagnoverse_Report_{uploaded_file.name}",
            mime="application/pdf",
            use_container_width=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
    
    result = st.session_state["result"]
    summary = result.get("summary", {})
    meds = result.get("medications", [])
    has_meds = len(meds) > 0 and any(m.get("name") for m in meds)
    
    # Setup tabs based on whether medications exist
    tab_titles = ["📋 Summary", "❓ Doctor Questions", "🔬 Extracted Data"]
    if has_meds:
        tab_titles.insert(1, "💊 Drug Insights")
        
    tabs = st.tabs(tab_titles)
    
    # ── TAB 1: Summary ──
    with tabs[0]:
        st.markdown("### 📋 Executive Summary")
        overview = summary.get("overview", "No overview available.")
        st.markdown(f'<div class="glass-card">{overview}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 🔍 Key Findings")
            findings = summary.get("key_findings", [])
            if findings:
                for f in findings:
                    st.markdown(f"- {f}")
            else:
                st.write("No specific key findings extracted.")
                
            st.markdown("#### ✅ Recommendations")
            recs = summary.get("recommendations", [])
            if recs:
                for r in recs:
                    st.markdown(f"- {r}")
            else:
                st.write("No specific recommendations provided.")
                
        with col2:
            st.markdown("#### ⚠️ Warnings")
            warnings = summary.get("warnings", [])
            if warnings:
                for w in warnings:
                    st.error(w)
            else:
                st.info("No major warnings detected.")
                
        st.markdown("#### 🧪 Lab Results")
        lab_data = summary.get("lab_table", [])
        if lab_data:
            # Render custom HTML table for lab data
            html_table = "<table><tr><th>Test</th><th>Value</th><th>Status</th></tr>"
            for row in lab_data:
                status = str(row.get("status", "")).strip().upper()
                status_class = "status-normal"
                if status == "HIGH":
                    status_class = "status-high"
                elif status == "LOW":
                    status_class = "status-low"
                    
                html_table += f"<tr><td>{row.get('test', '')}</td><td>{row.get('value', '')}</td><td class='{status_class}'>{row.get('status', '')}</td></tr>"
            html_table += "</table>"
            st.markdown(f'<div class="glass-card">{html_table}</div>', unsafe_allow_html=True)
        else:
            st.write("No lab results found in the report.")

    # ── TAB 2: Drug Insights (Conditional) ──
    tab_idx = 1
    if has_meds:
        with tabs[tab_idx]:
            st.markdown("### 💊 Medication Analysis")
            
            med_names = [m.get("name") for m in meds if m.get("name")]
            st.markdown(f"**Detected Medications:** {', '.join(med_names)}")
            
            d_col1, d_col2, d_col3 = st.columns(3)
            with d_col1:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("#### 🩺 Side Effects")
                side_effects = result.get("side_effects", [])
                if side_effects:
                    for s in side_effects:
                        st.markdown(f"- {s}")
                else:
                    st.write("None listed.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with d_col2:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("#### ⚠️ Drug Warnings")
                drug_warns = result.get("drug_warnings", [])
                if drug_warns:
                    for w in drug_warns:
                        st.markdown(f"- {w}")
                else:
                    st.write("None listed.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with d_col3:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("#### 🔗 Interactions")
                inter = result.get("drug_interactions", [])
                if inter:
                    for i in inter:
                        st.markdown(f"- {i}")
                else:
                    st.write("None listed.")
                st.markdown("</div>", unsafe_allow_html=True)
        tab_idx += 1

    # ── TAB 3: Doctor Questions ──
    with tabs[tab_idx]:
        st.markdown("### ❓ Questions for Your Doctor")
        st.write("Here are some personalized questions you might want to ask your doctor during your next visit:")
        
        questions = result.get("doctor_questions", [])
        if questions:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            for i, q in enumerate(questions, 1):
                st.markdown(f"**Q{i}.** {q}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No questions generated.")
    tab_idx += 1

    # ── TAB 4: Extracted Data ──
    with tabs[tab_idx]:
        st.markdown("### 🔬 Raw Extracted Data")
        with st.expander("View Conditions"):
            st.json(result.get("conditions", []))
        with st.expander("View Medications"):
            st.json(result.get("medications", []))
        with st.expander("View Lab Values"):
            st.json(result.get("lab_values", []))