import streamlit as st
import openai
import PyPDF2
import time

def run():
    st.subheader("Dhruv's Question Answering Chatbot")

    # Function to read PDF file
    def read_pdf(uploaded_file):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        num_pages = len(pdf_reader.pages)
        text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text

    # Initialize session state for conversation memory
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # OpenAI API key input
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    else:
        # Set up OpenAI client
        openai.api_key = openai_api_key

        try:
            # Validate API key
            openai.Model.list()
            st.success("API key is valid!", icon="✅")
        except:
            st.error("Invalid API key!!! Please try again.", icon="❌")
        else:
            # File uploader for the document
            uploaded_file = st.file_uploader(
                "Upload a document (.pdf or .txt)", type=("pdf", "txt"),
                accept_multiple_files=False,
                help="Supported formats: .pdf, .txt"
            )

            if uploaded_file is not None:
                if uploaded_file.type not in ("text/plain", "application/pdf"):
                    st.error("Unsupported file type. Please upload a .pdf or .txt file.")
                else:
                    # Process the uploaded file
                    if st.button("Process"):
                        try:
                            if uploaded_file.type == "text/plain":
                                document = uploaded_file.read().decode()
                            elif uploaded_file.type == "application/pdf":
                                document = read_pdf(uploaded_file)

                            st.session_state['document'] = document
                            st.success("File processed successfully!")
                        except Exception as e:
                            st.error("Error processing file. Please try again.")

                    # Chatbot functionality
                    question = st.chat_input("Ask a question about the document:")

                    if question:
                        # Display user's input in chat
                        st.chat_message("user").write(question)
                        st.session_state['messages'].append({"role": "user", "content": question})

                        if 'document' in st.session_state:
                            try:
                                # Include the conversation history in the prompt
                                conversation_history = st.session_state['messages']
                                messages = [{"role": "system", "content": f"Here's a document: {st.session_state['document']}"}] + conversation_history

                                # Stream the response
                                response = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=messages,
                                    stream=True
                                )

                                bot_message = ""
                                # Stream the response incrementally
                                for chunk in response:
                                    if "choices" in chunk:
                                        bot_message += chunk['choices'][0]['delta'].get('content', '')
                                        st.write(f"{bot_message}")
                                        time.sleep(0.05)  # Simulate typing effect

                                # Display the bot's response
                                st.chat_message("assistant").write(bot_message)
                                st.session_state['messages'].append({"role": "assistant", "content": bot_message})

                            except Exception as e:
                                st.error("Error generating answer. Please try again.")