import streamlit as st
import openai
import PyPDF2
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os

def create_chroma_db():
    # Initialize ChromaDB client with in-memory storage
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=":memory:"
    ))

    # Create OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=st.session_state.openai_api_key,
        model_name="text-embedding-3-small"
    )

    # Create collection
    collection = client.create_collection(
        name="Lab4Collection",
        embedding_function=openai_ef
    )

    # Read PDF files and add to collection
    pdf_dir = "pdf_files"  # Assuming PDF files are in a directory named 'pdf_files'
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            text = read_pdf(file_path)
            collection.add(
                documents=[text],
                metadatas=[{"filename": filename}],
                ids=[filename]
            )

    return collection

def read_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def test_vector_db(collection, query):
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    return [result['filename'] for result in results['metadatas'][0]]

def run():
    st.subheader("Lab 4 - Retrieval Augmented Generation (RAG)")

    # Initialize session state
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""

    # OpenAI API key input
    openai_api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        return

    # Set up OpenAI client
    openai.api_key = openai_api_key
    st.session_state.openai_api_key = openai_api_key

    try:
        # Validate API key
        openai.Model.list()
        st.success("API key is valid!", icon="✅")
    except:
        st.error("Invalid API key!!! Please try again.", icon="❌")
        return

    # Create ChromaDB collection if not already created
    if 'Lab4_vectorDB' not in st.session_state:
        st.session_state.Lab4_vectorDB = create_chroma_db()
        st.success("ChromaDB collection 'Lab4Collection' created successfully!")

    # Test the vector database
    st.subheader("Vector Database Test")
    test_query = st.selectbox("Select a test query:", ["Generative AI", "Text Mining", "Data Science Overview"])
    if st.button("Run Test Query"):
        results = test_vector_db(st.session_state.Lab4_vectorDB, test_query)
        st.write("Top 3 relevant documents:")
        for i, filename in enumerate(results, 1):
            st.write(f"{i}. {filename}")

    # Explanation of RAG and Vector Databases
    st.subheader("About Retrieval Augmented Generation (RAG)")
    st.write("""
    Retrieval Augmented Generation (RAG) is a technique that enhances language models by retrieving relevant information 
    from a knowledge base before generating a response. This approach combines the power of large language models with 
    the ability to access and utilize specific, up-to-date information.
    """)

    st.subheader("Vector Databases")
    st.write("""
    Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. 
    In the context of RAG:
    - They store embeddings, which are numerical representations of text, images, or other data.
    - Enable fast similarity searches to find the most relevant information for a given query.
    - Support various similarity metrics like Euclidean distance, cosine similarity, and dot product.
    """)

    st.subheader("ChromaDB")
    st.write("""
    ChromaDB is a vector database that:
    - Stores documents in collections (similar to tables in relational databases).
    - Uses embeddings to represent documents and queries.
    - Supports metadata for additional context and filtering.
    - Offers both local and client-server modes of operation.
    """)

if __name__ == "__main__":
    run()