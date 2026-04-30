from state.state import AgentState
from langchain_groq import ChatGroq
from typing import Literal
import requests
from agents.summary_agent import parse_json


from pydantic import BaseModel, Field
from typing import List

class DrugInfo(BaseModel):
    side_effects: List[str] = Field(description="Short common side effects")
    drug_warnings: List[str] = Field(description="Important safety warnings")
    drug_interactions: List[str] = Field(description="Major drug interactions")



model = ChatGroq(model="llama-3.1-8b-instant")

llm_structured = model.with_structured_output(DrugInfo)

def check_medics(state : AgentState) -> Literal["query_generator_agent","drug_checker_agent"]:
    if state['medications'] is not None and len(state['medications']) > 0:
        return "drug_checker_agent"
    else:
        return "query_generator_agent"
    

def normalize_drug_name(med_name:str):
    prompt = f"""
    Convert this medicine name into its generic drug name.

    Example:
    Crocin → Paracetamol
    Telma-AM → Telmisartan + Amlodipine

    Medicine:
    {med_name}

    Return only the generic name.
    """

    response = model.invoke(prompt)

    return response.content.strip()





def fetch_from_openfda(drug_name:str):
    url = "https://api.fda.gov/drug/label.json"

    params = {
        "search": f"openfda.generic_name:{drug_name}",
        "limit": 1
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        result = data["results"][0]

        return {
            "side_effects": result.get("adverse_reactions", [])[:1],
            "drug_warnings": result.get("warnings", [])[:1],
            "drug_interactions": result.get("drug_interactions", [])[:1]
        }

    except:
        return None
    

def llm_backup(drug_name:str):
        prompt = f"""
    You are a medical assistant.

    For the medicine below, give:
    - common side effects
    - important warnings
    - major drug interactions

    Medicine:
    {drug_name}

    Return ONLY JSON:

    {{
    "side_effects": [""],
    "drug_warnings": [""],
    "drug_interactions": [""]
    }}

    Rules:
    - Keep it short & simple
    - No extra explanation
    """

        response = model.invoke(prompt)
        return parse_json(response.content)

def clean_with_llm(raw_data):
    text = f"""
        Side Effects:
        {raw_data.get("side_effects", [])}

        Warnings:
        {raw_data.get("drug_warnings", [])}

        Interactions:
        {raw_data.get("drug_interactions", [])}
        """
    
    prompt = f"""
        Convert the following medical information into clean structured data.

        Rules:
        - Keep each point short (1 line)
        - Remove extra text or headings
        - No symbols (*, -, etc)
        - Only important points
        - Max 5 per category

        {text}
        """

    response = llm_structured.invoke(prompt)

    return response


# helper
def unique_list(items):
    seen = set()
    result = []
    for i in items:
        if i and i not in seen:
            seen.add(i)
            result.append(i)
    return result


def trim_text(text, max_chars=800):
    return text[:max_chars]



# ------------ DRUG AGENT --------------
def drug_checker_agent(state: AgentState) -> AgentState:

    medications = state.get("medications", [])

       # safety check
    if not medications or not any(m.get("name") for m in medications):
        state["side_effects"] = []
        state["drug_warnings"] = []
        state["drug_interactions"] = []
        return state

    all_side_effects = []
    all_warnings = []
    all_interactions = []

    # limit to avoid too many API calls
    medications = medications[:3]

    for med in medications:

        med_name = med.get("name", "")

        if not med_name:
            continue

        # Step 1: normalize
        generic_name = normalize_drug_name(med_name)

        # Step 2: try openFDA
        data = fetch_from_openfda(generic_name)

        raw_side = trim_text(" ".join(data.get("side_effects", [])))
        raw_warn = trim_text(" ".join(data.get("drug_warnings", [])))
        raw_inter = trim_text(" ".join(data.get("drug_interactions", [])))

        if data and any(data.values()):
            cleaned = clean_with_llm({
                "side_effects": raw_side,
                "drug_warnings": raw_warn,
                "drug_interactions": raw_inter
                })

        
        
        data = {
                "side_effects": cleaned.side_effects,
                "drug_warnings": cleaned.drug_warnings,
                "drug_interactions": cleaned.drug_interactions
            }

        # Step 3: fallback
        if not data or not any(data.values()):
            data = llm_backup(generic_name)

        # collect
        all_side_effects.extend(data.get("side_effects", []))
        all_warnings.extend(data.get("drug_warnings", []))
        all_interactions.extend(data.get("drug_interactions", []))

    # clean duplicates
    # final clean output
    state["side_effects"] = unique_list(all_side_effects)[:5]
    state["drug_warnings"] = unique_list(all_warnings)[:5]
    state["drug_interactions"] = unique_list(all_interactions)[:5]

    return state
