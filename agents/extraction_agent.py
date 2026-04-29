from langchain_community.document_loaders import PyMuPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
# Example: Using HuggingFace (Free)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
# from langchain_core.prompts import PromptTemplate                                                             
from langchain_groq import ChatGroq
from state.state import AgentState
from state.schema import MedicalEntities
# from agents.rag_helper_function import vector_store
from dotenv import load_dotenv
import tempfile

load_dotenv()

def extract_text(file_path):
    loader = PyMuPDFLoader(file_path)
    loaded_docs = loader.load()
    text = " ".join(doc.page_content for doc in loaded_docs)

    return text




def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,      # size of each chunk
        chunk_overlap=150     # overlap for better context
    )
    return splitter.split_text(text)




import json
import re

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
    return {
        "medications": [],
        "conditions": [],
        "lab_values": []
    }


def unique(items):
    seen = set()
    result = []

    for item in items:
        name = item.get("name", "").lower()

        if name and name not in seen:
            seen.add(name)
            result.append(item)

    return result



# complete_text = extract_text("../data/sample_pdf2.pdf")

def clean_text(text):
    # text = text.replace("\n"," ")
    text = " ".join(text.split())  #removes extra spaces
    return text 

# cleaned_text = clean_text(complete_text)
# print(complete_text,end="\n\n\n\t\n\n")
# print(cleaned_text)

def save_temp_file(uploaded_file):
    uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name
    



def load_vector_store():
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store = Chroma(
        persist_directory="vector_store",
        embedding_function=embedding,
        collection_name="medical_knowledge"
    )

    return vector_store


def get_rag_context(state, vector_store):

    queries = []

    # from lab values
    for lab in state["lab_values"]:
        queries.append(lab["name"])

    # from conditions
    for cond in state["conditions"]:
        queries.append(cond["name"])

    # from meds
    for med in state["medications"]:
        queries.append(med["name"])



    seen = set()
    context_chunks = []

    for q in queries:
        results = vector_store.similarity_search(q, k=2)
        # ensures the same chunk is not added multiple times repeatedly 
        for r in results:
            if r.page_content not in seen:
                seen.add(r.page_content)
                context_chunks.append(r.page_content)

    return "\n".join(context_chunks)











llm = ChatGroq(model="llama-3.1-8b-instant")
# model_with_schema = model.with_structured_output(MedicalEntities)


vector_store = load_vector_store()

#   ------------ EXTRACTION AGENT -----------------------

def extraction_agent(state: AgentState) -> AgentState:
    if state["input_type"] == "pdf":
        if isinstance(state["input_data"], str):
            file_path = state["input_data"]
    else:
        file_path = save_temp_file(state["input_data"])

    text = extract_text(file_path)

    state['extracted_text'] = text

    # cleaned text
    cleaned_text = clean_text(text)
    state["cleaned_text"] = cleaned_text 

    text = state["cleaned_text"]

    # 1. split text
    chunks = split_text(text)

    all_medications = []
    all_conditions = []
    all_lab_values = []

    # 2. loop through chunks
    for chunk in chunks:

        prompt = f"""
        Extract medical information from the report.

        Return ONLY valid JSON in this format:
        {{
        "medications": [{{"name": "", "description": ""}}],
        "conditions": [{{"name": "", "description": ""}}],
        "lab_values": [{{"name": "", "value": "", ref range: "", description": ""}}]
        }}

        Rules:
        - Only use information present
        - Do not guess 
        - If none exist, return []
        - Use "" for missing fields
        - No extra text
       Lab values:
        - Extract test name, RESULT value, and meaning if present
        - value must be the actual result (e.g., "0.7 mg/dl")
        - DO NOT use reference ranges (e.g., "0.66 - 1.25") for value 
        - add ref range from reference range column

        Medical Report:
        {chunk}
        """

        response = llm.invoke(prompt)

        data = parse_json(response.content)

        all_medications.extend(data.get("medications", []))
        all_conditions.extend(data.get("conditions", []))
        all_lab_values.extend(data.get("lab_values", []))

    # 3. remove duplicates
    state["medications"] = unique(all_medications)
    state["conditions"] = unique(all_conditions)
    state["lab_values"] = unique(all_lab_values)

    rag_context = get_rag_context(state, vector_store)

    state["rag_context"] = rag_context

    


    return state



