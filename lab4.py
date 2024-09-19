import streamlit as st
import openai
import PyPDF2
import chromadb
from chromadb.utils import embedding_functions

def create_and_test_vectordb(pdf_files):
    if 'Lab4_vectorDB' not in st.session_state:
        # Initialize ChromaDB client
        client = chromadb.Client()
        
        # Create OpenAI embedding function
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=st.session_state.openai_api_key,
            model_name="text-embedding-3-small"
        )
        
        # Create ChromaDB collection
        collection = client.create_collection(
            name="Lab4Collection",
            embedding_function=openai_ef
        )
        
        # Add documents to the collection
        for pdf_file in pdf_files:
            text = read_pdf(pdf_file)
            collection.add(
                documents=[text],
                metadatas=[{"filename": pdf_file.name}],
                ids=[pdf_file.name]
            )
        
        # Store the collection in session state
        st.session_state.Lab4_vectorDB = collection
    
    # Test the vectorDB
    test_queries = ["Generative AI", "Text Mining", "Data Science Overview"]
    for query in test_queries:
        results = st.session_state.Lab4_vectorDB.query(
            query_texts=[query],
            n_results=3
        )
        st.subheader(f"Top 3 documents for query: '{query}'")
        for i, doc in enumerate(results['metadatas'][0], 1):
            st.write(f"{i}. {doc['filename']}")
        st.write("---")

def run():
    st.subheader("Dhruv's Question Answering Chatbot")

    # Function to read PDF file
    def read_pdf(uploaded_file):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'document' not in st.session_state:
        st.session_state['document'] = None
    if 'waiting_for_more_info' not in st.session_state:
        st.session_state['waiting_for_more_info'] = False

    # OpenAI API key input
    openai_api_key = st.text_input("OpenAI API Key", type="password")
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

    # File uploader for multiple PDF files
    uploaded_files = st.file_uploader(
        "Upload PDF documents", type="pdf", accept_multiple_files=True,
        help="Upload up to 7 PDF files"
    )

    if uploaded_files and len(uploaded_files) == 7:
        if st.button("Process and Test VectorDB"):
            create_and_test_vectordb(uploaded_files)
    elif uploaded_files:
        st.warning("Please upload exactly 7 PDF files.")

    # ... (rest of the existing code)

if __name__ == "__main__":
    run()