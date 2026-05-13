# 🧠 Diagnoverse AI

> Transforming Medical Reports into Intelligent Insights.

Diagnoverse AI is an AI-powered medical report analysis platform designed to help users better understand complex medical reports through intelligent summaries, lab analysis, drug insights, and conversational AI assistance.

The system combines:

* Multi-agent AI workflows
* Retrieval-Augmented Generation (RAG)
* Medical knowledge retrieval
* Drug safety analysis
* AI-generated patient-friendly summaries
* Interactive chatbot assistance
* PDF report export

---

# ✨ Features

## 📄 Medical Report Analysis

Upload medical reports in PDF format and receive:

* Simplified patient-friendly summaries
* Important findings
* Warnings and abnormalities
* Structured lab value extraction
* Doctor question suggestions

---

## 🧪 Intelligent Lab Analysis

Diagnoverse AI extracts and analyzes:

* Blood test values
* Kidney function markers
* Liver function markers
* Cholesterol levels
* Vitamins and minerals
* Electrolytes
* CBC values
* PSA and other biomarkers

The system attempts to compare extracted values against reference ranges and identify abnormalities.

---

## 💊 Drug Insight Engine

The application includes a conditional drug-checking pipeline that:

* Detects medications from reports
* Normalizes medicine names
* Uses OpenFDA data when available
* Provides:

  * Side effects
  * Drug warnings
  * Drug interactions

Fallback LLM-based handling is also included when API data is unavailable.

---

## 🤖 AI Chat Assistant

Diagnoverse AI includes a conversational chatbot assistant that:

* Maintains short-term memory
* Provides medical report guidance
* Becomes context-aware after report upload
* Explains medical terms in simple language
* Helps users better understand their reports

---

## 📚 Retrieval-Augmented Generation (RAG)

The platform uses a medical knowledge base combined with vector search to provide:

* Better explanations
* Context-aware summaries
* More meaningful insights
* Reduced hallucinations

The knowledge base currently includes:

* Diabetes markers
* Cholesterol information
* Kidney markers
* Liver markers
* Vitamins
* Electrolytes
* Medication information

---

## 📥 PDF Export

Users can download AI-generated report summaries and insights in PDF format.

---

# 🏗️ System Architecture

Diagnoverse AI follows a multi-agent workflow architecture powered by LangGraph.

## Workflow Overview

```text
PDF Upload
    ↓
Extraction Agent
    ├── Summary Agent 
    ├── Query Generator Agent 
    └── Drug Checker Agent (Conditional)
    ↓
Final Structured Output
    ↓
Dashboard + Chatbot + PDF Export
```

---

# ⚙️ Tech Stack

## 🧠 AI / LLM

* LangChain
* LangGraph
* Groq API
* Llama 3.1 8B Instant

## 📚 RAG & Embeddings

* ChromaDB
* HuggingFace Embeddings
* sentence-transformers/all-MiniLM-L6-v2

## 🌐 Frontend

* Streamlit
* Custom CSS

## 🛠️ Backend

* Python

## 💊 External APIs

* OpenFDA API

---

# 📁 Project Structure

```text
Diagnoverse-AI/
│   ├── __init__.py
│   ├── extraction_agent.py          # Extracts text, lab values, medications, conditions
│   ├── summary_agent.py             # Generates patient-friendly summaries
│   ├── query_gen_agent.py           # Generates doctor/patient follow-up questions
│   ├── drug_checker_agent.py        # Drug safety, interactions, side effects
│   ├── rag_helper_function.py       # RAG retrieval helper utilities
│   └── test.ipynb                   # Testing and experimentation notebook
│
├── app/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── graph.py                     # LangGraph workflow architecture
│   ├── ui.py                        # Main Streamlit frontend application
│   └── pdf_export.py                # PDF generation/export utilities
│
├── dataset/
│   └── medical_knowledge.txt        # Medical knowledge base for RAG
│
├── images/
│   ├── chatbot_white.png
│   └── diagnoverse_white.png
│
├── mvenv/                           # Virtual environment
│
├── state/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── prompts.txt                  # Prompt templates
│   ├── schema.py                    # Structured output schemas
│   └── state.py                     # Shared LangGraph state definitions
│
├── vector_store/
│   ├── chroma.sqlite3
│   └── <chroma vector DB files>
│
├── input_data/                      # Sample uploaded reports
│
├── .env                             # Environment variables
├── .gitignore
├── requirement.txt
└── README.md
```

---

# 🚀 Installation

## 1️⃣ Clone Repository

```bash
git clone <your-repository-url>
cd Diagnoverse-AI
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv mvenv
mvenv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv mvenv
source mvenv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Setup Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

---

## 5️⃣ Run Application

```bash
streamlit run app/ui.py
```

---

# 🧠 How It Works

## 1. Extraction Agent

Responsible for:

* Extracting text from uploaded reports
* Identifying:

  * conditions
  * medications
  * lab values
* Preparing RAG retrieval queries

---

## 2. Summary Agent

Generates:

* Patient-friendly overview
* Key findings
* Warnings
* Recommendations
* Lab result tables

---

## 3. Query Generator Agent

Creates useful patient-focused questions such as:

* What precautions should I take?
* Which results are abnormal?
* Should I consult a specialist?

---

## 4. Drug Checker Agent

Conditional agent that activates only when medications are detected.

Provides:

* Side effects
* Warnings
* Drug interactions

---

## 5. Chat Assistant

Provides conversational AI interaction with:

* Conversation memory
* Context-aware responses
* Medical explanation assistance

---

# 🎨 UI Highlights

Diagnoverse AI includes:

* Premium futuristic dashboard
* Dark AI-themed UI
* Animated sections
* Glassmorphism-inspired design
* Floating chatbot assistant
* Interactive analysis panels
* Responsive layout

---

# 🔒 Important Disclaimer

Diagnoverse AI is an educational and informational AI assistant.

It is NOT a replacement for:

* licensed doctors
* medical diagnosis
* professional healthcare advice

Always consult a qualified healthcare professional for medical decisions.

---

# 📈 Future Improvements

Planned upgrades include:

* OCR support for scanned reports
* Advanced medical knowledge base
* Smarter report-aware chatbot
* Real-time medical search integration
* Streaming AI responses
* Better lab extraction accuracy
* Multi-language support
* User authentication
* Cloud deployment

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and submit pull requests.

---

# 📜 License

This project is intended for educational and research purposes.

---

# 👨‍💻 Author

Developed by Mir Haroon Ali.

---

# 🌌 Diagnoverse AI

> Making medical reports understandable through AI.
