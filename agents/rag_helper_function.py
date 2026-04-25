from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def build_vector_store():
    with open("dataset/medical_knowledge.txt", "r") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    docs = splitter.create_documents([text])

    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store = Chroma.from_documents(
        docs,
        embedding=embedding,
        persist_directory="vector_store",
        collection_name="medical_knowledge"
    )
     
    print("store knowledge base !")

    return vector_store

vector_store = build_vector_store()