import streamlit as st
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
import os
import toml

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Load API keys from secrets.toml
secrets_path = os.path.join(".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)

# Initialize OpenAI client
openai_client = OpenAI(api_key=secrets['openai_api_key'])

# Function to create ChromaDB collection
def create_chromadb_collection(pdf_files):
    if 'Lab4_vectorDB' not in st.session_state:
        # Initialize ChromaDB Persistent Client
        chroma_client = chromadb.PersistentClient()

        # Get or create collection named Lab4Collection
        collection = chroma_client.get_or_create_collection(name="Lab4Collection")

        # Set up OpenAI embedding function
        openai_embedder = embedding_functions.OpenAIEmbeddingFunction(
            api_key=secrets['openai_api_key'], 
            model_name="text-embedding-ada-002"
        )

        # Read PDFs and add to the collection
        for file in pdf_files:
            pdf_text = ""
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()

            collection.add(
                documents=[pdf_text],
                metadatas=[{"filename": file.name}],
                ids=[file.name]
            )

        st.session_state['Lab4_vectorDB'] = collection
        st.success("ChromaDB collection has been created!")
    else:
        st.info("Collection already created in session.")

# Function to query the collection and get related documents
def get_relevant_documents(query):
    if 'Lab4_vectorDB' in st.session_state:
        collection = st.session_state['Lab4_vectorDB']
        # Get the embedding for the query
        response = openai_client.embeddings.create(input=query, model="text-embedding-ada-002")
        query_embedding = response.data[0].embedding

        # Query ChromaDB collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        context = ""
        for i, doc in enumerate(results['documents'][0]):
            doc_id = results['ids'][0][i]
            context += f"Document '{doc_id}': {doc[:300]}...\n\n"

        return context
    else:
        return "No ChromaDB collection is available."

# Streamlit app layout
def run():
    st.title("Lab 4: Course Understanding")

    # Sidebar for PDF Upload
    pdf_files = st.sidebar.file_uploader("Upload PDF files", accept_multiple_files=True, type=["pdf"])
    if st.sidebar.button("Create ChromaDB") and pdf_files:
        create_chromadb_collection(pdf_files)

    # Question Input
    query = st.text_input("Ask a question about the PDFs:")
    if query:
        st.session_state['messages'].append({"role": "user", "content": query})

        context = get_relevant_documents(query)

        # Display query result context
        st.markdown(f"### Relevant Context: \n{context}")

        # Generating response with OpenAI
        messages = [
            {"role": "system", "content": f"Use the following context to answer questions: {context}"},
            {"role": "user", "content": query}
        ]
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        answer = response.choices[0].message['content']

        # Display Answer
        st.markdown(f"### Answer: \n{answer}")
        st.session_state['messages'].append({"role": "assistant", "content": answer})

    # Display conversation history
    st.subheader("Conversation History")
    for message in st.session_state['messages']:
        with st.expander(message["role"]):
            st.markdown(message["content"])

if __name__ == "__main__":
    run()