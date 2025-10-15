from uuid import uuid4
from pathlib import Path
import streamlit as st

# ✅ Use community versions for loaders, vectorstores, and embeddings
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

# ✅ Chain and prompt utilities remain same
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate


# ==========================
# 🔑 API Keys and Constants
# ==========================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

CHUNK_SIZE = 1000
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME = "real_estate"

llm = None
vector_store = None


# ==========================
# ⚙️ Initialization
# ==========================
def initialize_components():
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.9, max_tokens=500)

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTORSTORE_DIR)
        )


# ==========================
# 🌐 Process URLs
# ==========================
def process_urls(urls):
    """
    This function scrapes data from URLs and stores it in a vector database.
    """
    yield "Initializing Components..."
    initialize_components()

    yield "Resetting vector store...✅"
    vector_store.reset_collection()

    yield "Loading data...✅"
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()

    yield "Splitting text into chunks...✅"
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=CHUNK_SIZE
    )
    docs = text_splitter.split_documents(data)

    yield "Adding chunks to vector database...✅"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=uuids)

    yield "Documents successfully added to vector database...✅"


# ==========================
# 💬 Generate Answer
# ==========================
def generate_answer(query):
    if not vector_store:
        raise RuntimeError("Vector database is not initialized.")

    # 🧠 Define prompt
    prompt = ChatPromptTemplate.from_template(
        "Use the following context to answer the question accurately.\n\n"
        "Context:\n{context}\n\n"
        "Question: {input}"
    )

    # 🧩 Create chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(vector_store.as_retriever(), document_chain)

    # 🚀 Run query
    result = retrieval_chain.invoke({"input": query})
    answer = result.get("answer", "No answer found.")

    return answer


# ==========================
# 🧪 Test Run (Optional)
# ==========================
if __name__ == "__main__":
    urls = [
        "https://timesproperty.com/news/post/demand-boosts-kolkata-real-estate-prices-by-8-pc-in-q3-2025-blid10734",
        "https://maxestates.in/residential-projects-in-gurgaon-meets-conscious-luxury"
    ]

    for status in process_urls(urls):
        print(status)

    answer = generate_answer("How much energy do IGBC-certified green buildings in India save?")
    print(f"\nAnswer: {answer}")
