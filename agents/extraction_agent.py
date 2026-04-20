from langchain_community.document_loaders import PyMuPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
# Example: Using HuggingFace (Free)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from state.state import AgentState
from state.schema import MedicalEntities
from dotenv import load_dotenv
import tempfile

load_dotenv()

def extract_text(file_path):
    loader = PyMuPDFLoader(file_path)
    loaded_docs = loader.load()
    text = " ".join(doc.page_content for doc in loaded_docs)

    return text

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







model = ChatGroq(model="llama-3.1-8b-instant")
model_with_schema = model.with_structured_output(MedicalEntities)






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

    # with open("state/prompt.txt", "r") as f:
    #     prompt_template = f.read()

    # prompt = prompt_template.format(input_text=state["cleaned_text"])

    prompt = f""" Extract medical entities from the report:

    - Medications (only actual drugs/medicines, not lab materials or supplements unless clearly prescribed)
    - Conditions (disease names + brief explanation if mentioned)
    - Lab values (test name + value if present + meaning if mentioned)

    Rules:
    - Only extract what is present
    - Do not guess
    - If no items exist, return empty list []
    - Ensure output matches the schema exactly
    - Exclude lab sample types (e.g., NaF blood)

    Medical Report:
    {state['cleaned_text']} """

    response = model_with_schema.invoke(prompt)

    print(response, end="\n\n\t\t\n\n\t\n\n")

    state["medications"] = [m.model_dump() for m in response.medications]
    state["conditions"] = [c.model_dump() for c in response.conditions]
    state["lab_values"] = [l.model_dump() for l in response.lab_values]



    return state



