# from matplotlib.pyplot import colorbar
from sympy import false
import streamlit as st
import sys
import os
import tempfile
import json
from langchain_groq import ChatGroq

# Fix import paths to allow importing from agents, state, etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph import workflow
from app.pdf_export import generate_pdf
import base64

# ── Page Configuration ─────────────────────────────────────────────────────────
icon_path = os.path.join(os.path.dirname(__file__), "..", "images", "diagnoverse_white.png")
try:
    from PIL import Image
    page_icon = Image.open(icon_path)
except Exception:
    page_icon = icon_path

st.set_page_config(page_title="Diagnoverse AI", page_icon=page_icon, layout="wide", initial_sidebar_state="collapsed")

# ── Custom CSS for Premium Dark Glassmorphism & Animations ──────────────────
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap');

    /* Global Background */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(0, 212, 170, 0.05), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(130, 100, 235, 0.05), transparent 25%);
        color: #f0f2f8;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers & Text */
    h1, h2, h3, h4, p, span, li {
        color: #f0f2f8 !important;
        font-family: 'Outfit', sans-serif;
    }
    p, span, li {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 4rem 2rem 2rem 2rem;
        animation: fadeIn 1s ease-in-out;
    }
    
    .hero-title {
        background: linear-gradient(135deg, #00d4aa 0%, #00b38f 50%, #8264eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #a0aec0 !important;
        font-weight: 300;
        margin-bottom: 2rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Cards (Glassmorphism) */
    .glass-card {
        background: rgba(25, 30, 45, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.2);
    }
    
    /* Alert styling */
    .stAlert {
        background: rgba(25, 30, 45, 0.6) !important;
        border: 1px solid rgba(0, 212, 170, 0.3) !important;
        border-radius: 12px !important;
        color: #f0f2f8 !important;
        backdrop-filter: blur(10px);
    }
    
    /* Primary Analyze Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #00d4aa 0%, #009688 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.5);
    }
    
    /* Prominent PDF Download Button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #8264eb 0%, #5e35b1 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 1rem;
        width: 100%;
        margin-top: 10px;
        box-shadow: 0 4px 15px rgba(130, 100, 235, 0.4);
        transition: all 0.3s ease;
    }
    .stDownloadButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(130, 100, 235, 0.6);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: rgba(25, 30, 45, 0.6);
        border-radius: 12px 12px 0px 0px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: none;
        padding: 10px 24px;
        font-weight: 500;
        font-family: 'Outfit', sans-serif;
        color: #a0aec0 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 212, 170, 0.1);
        border-top: 3px solid #00d4aa;
        color: #00d4aa !important;
    }
    
    /* Table Styling */
    table {
        width: 100%;
        color: #f0f2f8;
        border-collapse: collapse;
        margin-top: 10px;
    }
    th {
        background-color: rgba(0, 212, 170, 0.1);
        text-align: left;
        padding: 14px;
        color: #00d4aa !important;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    td {
        padding: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    tr:hover td {
        background-color: rgba(255, 255, 255, 0.02);
    }
    
    /* Status pills */
    .status-normal { color: #48c78e; font-weight: 700; background: rgba(72, 199, 142, 0.1); padding: 4px 8px; border-radius: 12px;}
    .status-high { color: #ff6b6b; font-weight: 700; background: rgba(255, 107, 107, 0.1); padding: 4px 8px; border-radius: 12px;}
    .status-low { color: #ffa726; font-weight: 700; background: rgba(255, 167, 38, 0.1); padding: 4px 8px; border-radius: 12px;}
    
    /* File Uploader override */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(25, 30, 45, 0.6) !important;
        border: 2px dashed rgba(0, 212, 170, 0.3) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #00d4aa !important;
        background-color: rgba(0, 212, 170, 0.05) !important;
    }

    /* Chatbot Floating Button (Targeting specific key if possible, else we rely on columns) */
    .st-key-chat_toggle_btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }
    .st-key-chat_toggle_btn button {
        width: 65px;
        height: 65px;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 24px;
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.5) !important;
    }
    
    /* Chatbot Window Container */
    .st-key-chat_window_container {
        position: fixed;
        bottom: 110px;
        right: 30px;
        width: 380px;
        max-width: 90vw;
        height: 500px;
        z-index: 9998;
        background: rgba(15, 20, 30, 0.95);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        padding: 15px;
        overflow-y: auto;
        animation: slideUp 0.3s ease-out;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Hero Logo Standard Size */
    .hero-logo {
        width: 70px;
        vertical-align: middle;
        margin-right: 15px;
        margin-bottom: 15px;
    }

    /* ── Responsive Design for Mobile ── */
    @media (max-width: 768px) {
        .hero-container {
            padding: 2rem 1rem 1rem 1rem;
        }
        .hero-title {
            font-size: 2.2rem;
            line-height: 1.2;
        }
        .hero-logo {
            width: 45px;
            margin-right: 10px;
            margin-bottom: 8px;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }
        .glass-card {
            padding: 16px;
        }
        
        /* Chatbot adjustments */
        .st-key-chat_toggle_btn {
            bottom: 20px;
            right: 20px;
        }
        .st-key-chat_toggle_btn button {
            width: 55px;
            height: 55px;
        }
        .st-key-chat_window_container {
            width: 90vw;
            height: 450px;
            bottom: 90px;
            right: 5vw;
        }
        
        /* Tables & Tabs */
        .stTabs [data-baseweb="tab"] {
            padding: 10px 12px;
            font-size: 0.9rem;
        }
        th, td {
            padding: 10px;
            font-size: 0.9rem;
        }
        
        /* Upload box */
        [data-testid="stFileUploadDropzone"] {
            padding: 1rem !important;
        }
    }
</style>
"""

# Inject CSS
st.markdown(custom_css, unsafe_allow_html=True)

# ── Inject Chatbot Button Icon via Base64 ──────────────────────────────────────
try:
    chatbot_icon_path = os.path.join(os.path.dirname(__file__), "..", "images", "chatbot_white.png")
    with open(chatbot_icon_path, 'rb') as f:
        chatbot_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
        .st-key-chat_toggle_btn button {{
            font-size: 0px !important;
            color: transparent !important;
            background-image: url("data:image/png;base64,{chatbot_b64}");
            background-size: 55%;
            background-repeat: no-repeat;
            background-position: center;
        }}
    </style>
    """, unsafe_allow_html=True)
except Exception as e:
    pass

# ── Session State Initialization ───────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state["result"] = None
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
if "chat_open" not in st.session_state:
    st.session_state["chat_open"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am Diagnoverse AI. How can I help you understand your medical report today?"}
    ]

# ── Hero Section ───────────────────────────────────────────────────────────────
try:
    diagnoverse_icon_path = os.path.join(os.path.dirname(__file__), "..", "images", "diagnoverse_white.png")
    with open(diagnoverse_icon_path, 'rb') as f:
        diag_b64 = base64.b64encode(f.read()).decode()
    hero_title_html = f'<img class="hero-logo" src="data:image/png;base64,{diag_b64}">DIAGNOVERSE AI'
except Exception:
    hero_title_html = "DIAGNOVERSE AI"

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">{hero_title_html}</div>
    <div class="hero-subtitle">Transforming Medical Reports into Intelligent Insights</div>
</div>
""", unsafe_allow_html=True)

# ── Upload Zone ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("📄 Upload your medical report (PDF)", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        st.info(f"✨ File ready: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        analyze_btn = st.button("Analyze Report", use_container_width=True)

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

# ── Floating Chatbot Helper ────────────────────────────────────────────────────
chat_llm = ChatGroq(model="llama-3.1-8b-instant")

# Chat Toggle Button
if st.button(" ", key="chat_toggle_btn", help="Toggle AI Assistant"):
    st.session_state["chat_open"] = not st.session_state["chat_open"]

# Render Chat Window if open
if st.session_state["chat_open"]:
    with st.container(key="chat_window_container"):
        st.markdown("<h4 style='text-align: center; color: #00d4aa; margin-top: 0;'>Ask Diagnoverse AI</h4>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # Display chat messages
        chat_history_container = st.container(height=350, border=False)
        with chat_history_container:
            for msg in st.session_state["messages"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                
        # Chat input at the bottom of the container
        if prompt := st.chat_input("Type your medical query...", key="floating_chat_input"):
            st.session_state["messages"].append({"role": "user", "content": prompt})
            
            with chat_history_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            # Build context
                            sys_prompt = "You are a helpful medical AI assistant named Diagnoverse AI. Keep your answers concise, empathetic, and professional. "
                            if st.session_state.get("result"):
                                overview = st.session_state.get("result", {}).get("summary", {}).get("overview", "")
                                if overview:
                                    sys_prompt += f"The user has uploaded a medical report. Summary: {overview}. Base your answers on this context if relevant."
                            
                            msgs_for_llm = [("system", sys_prompt)]

                            # only recent memory
                            recent_messages = st.session_state["messages"][-8:]

                            for m in recent_messages:
                                msgs_for_llm.append((m["role"], m["content"]))
                                
                            response = chat_llm.invoke(msgs_for_llm)
                            st.markdown(response.content)
                            st.session_state["messages"].append({"role": "assistant", "content": response.content})
                        except Exception as e:
                            st.error(f"Error communicating with AI: {e}")

# ── Results Dashboard ──────────────────────────────────────────────────────────
if st.session_state["result"] is not None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    result = st.session_state["result"]
    summary = result.get("summary", {})
    meds = result.get("medications", [])
    has_meds = len(meds) > 0 and any(m.get("name") for m in meds)
    
    # ── Prominent Download Button ──
    if st.session_state["pdf_bytes"] is not None:
        dl_col1, dl_col2, dl_col3 = st.columns([1, 2, 1])
        with dl_col2:
            st.download_button(
                label="📄 DOWNLOAD PREMIUM PDF REPORT",
                data=st.session_state["pdf_bytes"],
                file_name=f"Diagnoverse_Report_{uploaded_file.name}",
                mime="application/pdf",
                use_container_width=True
            )
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Define tabs
    tab_titles = [
        "📋 Overview & Findings",
        "🧪 Lab Results",
        "💊 Drug Insights",
        "❓ Questions For Doctor",
        "🔬 Raw Data"
    ]
    tabs = st.tabs(tab_titles)
    
    # ── TAB 1: Overview & Findings ──
    with tabs[0]:
        st.markdown("<br>", unsafe_allow_html=True)
        overview = summary.get("overview", "No overview available.")
        st.markdown(f'<div class="glass-card"><h4>Executive Summary</h4><p>{overview}</p></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🔍 Key Findings")
            findings = summary.get("key_findings", [])
            if findings:
                for f in findings:
                    st.markdown(f"- {f}")
            else:
                st.write("No specific key findings extracted.")
            st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### ✅ Recommendations")
            recs = summary.get("recommendations", [])
            if recs:
                for r in recs:
                    st.markdown(f"- {r}")
            else:
                st.write("No specific recommendations provided.")
            st.markdown('</div>', unsafe_allow_html=True)
                
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### ⚠️ Warnings")
            warnings = summary.get("warnings", [])
            if warnings:
                for w in warnings:
                    st.error(w)
            else:
                st.info("No major warnings detected.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 2: Lab Results ──
    with tabs[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        lab_data = summary.get("lab_table", [])
        if lab_data:
            html_table = "<table><tr><th>Test Name</th><th>Value</th><th>Status</th></tr>"
            for row in lab_data:
                status = str(row.get("status", "")).strip().upper()
                status_class = "status-normal"
                if status == "HIGH":
                    status_class = "status-high"
                elif status == "LOW":
                    status_class = "status-low"
                    
                html_table += f"<tr><td>{row.get('test', '')}</td><td>{row.get('value', '')}</td><td><span class='{status_class}'>{row.get('status', '')}</span></td></tr>"
            html_table += "</table>"
            st.markdown(f'<div class="glass-card">{html_table}</div>', unsafe_allow_html=True)
        else:
            st.info("No lab results found in the report.")

    # ── TAB 3: Drug Insights ──
    with tabs[2]:
        st.markdown("<br>", unsafe_allow_html=True)
        if has_meds:
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
        else:
            st.info("No medications found in the report.")

    # ── TAB 4: Doctor Questions ──
    with tabs[3]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("Here are some personalized questions you might want to ask your doctor during your next visit:")
        
        questions = result.get("doctor_questions", [])
        if questions:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            for i, q in enumerate(questions, 1):
                st.markdown(f"**Q{i}.** {q}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No questions generated.")

    # ── TAB 5: Raw Data ──
    with tabs[4]:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("View Extracted Conditions"):
            st.json(result.get("conditions", []))
        with st.expander("View Extracted Medications"):
            st.json(result.get("medications", []))
        with st.expander("View Raw Lab Values"):
            st.json(result.get("lab_values", []))

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True) # Bottom padding for floating chat
