from state.state import AgentState
from langchain_groq import ChatGroq
import json
import re

def parse_list(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return []

llm = ChatGroq(model="llama-3.1-8b-instant")


def query_generator_agent(state:AgentState ) -> AgentState:
    prompt = """ You are a helpful medical assistant.

    Based on the patient's medical report, generate 5 to 7 simple and important questions the patient should ask their doctor.

    Focus on:
    - understanding their condition
    - precautions and lifestyle changes
    - risks and complications
    - treatment or next steps

    Rules:
    - Keep questions simple and easy to understand
    - Do NOT use heavy medical jargon
    - Do NOT give answers, only questions

    Patient Data:
    Conditions: {state["conditions"]}
    Lab Values: {state["lab_values"]}

    Additional Context:
    {state["rag_context"]}

    Return ONLY a JSON list of questions like:
    ["question 1", "question 2"]
    """

    response = llm.invoke(prompt)

    quests = parse_list(response.content)

    state["doctor_questions"] = quests

    return state