#frontend
import streamlit as st
import sys
import os
import tempfile



# fix import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph import workflow  # your compiled graph

st.set_page_config(page_title="Medical Report Analyzer", layout="wide")

st.title("🧠 Medical Report Analyzer")
st.write("Upload your report and get insights instantly.")

uploaded_file = st.file_uploader("📄 Upload your medical report (PDF)", type=["pdf"])

# save uploaded file
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    tmp.write(uploaded_file.getvalue()) 
    temp_path = tmp.name

if uploaded_file:

    st.info("⏳ This may take 1–2 minutes depending on report size")

    if st.button("Analyze Report"):

        with st.spinner("Analyzing report..."):
            st.session_state["result"] = workflow.invoke({
                "input_type": "pdf",
                "input_data": uploaded_file,
                "file_name": uploaded_file.name
            })

if "result" in st.session_state:
        
    st.success("✅ Analysis Complete")

    result = st.session_state["result"]
    summary = result.get("summary", {})

    st.subheader("🧾 Overview")
    st.write(summary.get("overview", "No overview available"))

    st.subheader("📌 Key Findings")

    for item in summary.get("key_findings", []):
        st.markdown(f"- {item}")


    st.subheader("📊 Lab Results")

    lab_data = summary.get("lab_table", [])

    if lab_data:
        st.table(lab_data)
    else:
        st.write("No lab data available")


    st.subheader("⚠️ Warnings")

    for w in summary.get("warnings", []):
        st.markdown(f"- {w}")

    st.subheader("💊 Drug Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Side Effects")
        for s in result.get("side_effects", []):
            st.markdown(f"- {s}")

    with col2:
        st.write("Warnings")
        for w in result.get("drug_warnings", []):
                st.markdown(f"- {w}")

    with col3:
        st.write("Interactions")
        for i in result.get("drug_interactions", []):
                st.markdown(f"- {i}")

    st.json(result)