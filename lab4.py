__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import openai
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import os

# Set up OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

# Function to read PDF files
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to create ChromaDB collection
def create_chroma_collection():
    # Create ChromaDB client
    client = chromadb.Client()
    
    # Create OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai.api_key,
        model_name="text-embedding-3-small"
    )
    
    # Create collection
    collection = client.create_collection(
        name="Lab4Collection",
        embedding_function=openai_ef
    )
    
    # Process PDF files
    pdf_dir = "pdf_files"  # Directory containing PDF files
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            text = read_pdf(file_path)
            
            # Add document to collection
            collection.add(
                documents=[text],
                metadatas=[{"filename": filename}],
                ids=[filename]
            )
    
    return collection

# Function to get or create vector database
def get_or_create_vectordb():
    if 'Lab4_vectorDB' not in st.session_state:
        st.session_state.Lab4_vectorDB = create_chroma_collection()
    return st.session_state.Lab4_vectorDB

# Function to search vector database
def search_vectordb(query, k=3):
    collection = get_or_create_vectordb()
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results

# Function to generate response using OpenAI
def generate_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message['content']

# Streamlit app
def main():
    st.title("Course Information Chatbot")

    # Initialize vector database
    vectordb = get_or_create_vectordb()

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about the course"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Search vector database
        search_results = search_vectordb(prompt)

        # Prepare context for the LLM
        context = "Based on the following information from course documents:\n\n"
        for doc, metadata in zip(search_results['documents'][0], search_results['metadatas'][0]):
            context += f"From {metadata['filename']}:\n{doc}\n\n"

        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions about a course based on the provided information. If the information is not in the context, say so."},
            {"role": "user", "content": f"{context}\n\nQuestion: {prompt}"}
        ]

        # Generate response
        with st.chat_message("assistant"):
            response = generate_response(messages)
            st.markdown(response)

        # Add assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()