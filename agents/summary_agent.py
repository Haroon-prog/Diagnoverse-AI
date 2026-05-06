from state.state import AgentState
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
import json, re

llm = ChatGroq(model="llama-3.1-8b-instant")

try:
    search_tool = DuckDuckGoSearchRun()
except:
    search_tool = None



def parse_json(text):
    
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {}



def summary_agent(state: AgentState) -> AgentState:
     
    lab_values = state.get("lab_values", [])
    search_context = ""
    
    # Pre-fetch missing reference ranges using web search
    if search_tool:
        for lab in lab_values:
            ref = lab.get("ref_range", "").strip()
            name = lab.get("name", "").strip()
            if name and not ref:
                try:
                    res = search_tool.invoke(f"normal reference range for {name} blood test adult")
                    search_context += f"Web Search for '{name}': {res}\n"
                except Exception:
                    pass

    prompt = f"""
    You are a helpful medical assistant.

    Create a simple summary of the patient's report.

    Conditions:
    {state.get('conditions', [])}

    Lab Values:
    {lab_values[:12]}

    RAG Context:
    {state.get('rag_context', '')}
    
    Web Search Context (for missing reference ranges):
    {search_context}

    Return ONLY JSON:

    {{
    "overview": "",
    "key_findings": [""],
    "lab_table": [
        {{"test": "", "value": "", "status": ""}}
    ],
    "warnings": [""],
    "recommendations": [""]
    }}

    Rules:
    - Use very simple everyday language
    - Explain conditions in 1 short phrase if needed, No medical jargon 
    - For `status` in `lab_table`:
        1. First, use the `ref_range` provided in the Lab Values.
        2. If missing, use the RAG Context.
        3. If still missing, use the Web Search Context provided.
        4. If still missing, use your general medical knowledge.
    - `status` MUST be EXACTLY one of: "Normal", "High", "Low", or "Unknown"
    """

    response = llm.invoke(prompt).content

    result = parse_json(response)

    return {'summary':result}