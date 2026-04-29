from state.state import AgentState
from langchain_groq import ChatGroq
import json, re

llm = ChatGroq(model="llama-3.1-8b-instant")


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
     
    prompt = f"""
        

    You are a helpful medical assistant.

    Create a simple summary of the patient's report.

    Conditions:
    {state['conditions']}

    Lab Values:
    {state['lab_values']}

    Context:
    {state['rag_context']}

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
    - Explain conditions in 1 short phrase if needed,No medical jargon 
    - give status based on ref range from the report , if present in report or else do google search for particular value .
    - status should be from these only (Normal / High / Low)
    """

    response = llm.invoke(prompt).content

    result = parse_json(response)

    return {'summary':result}