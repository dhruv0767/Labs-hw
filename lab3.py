import streamlit as st
import openai
import PyPDF2

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

    try:
        # Validate API key
        openai.Model.list()
        st.success("API key is valid!", icon="✅")
    except:
        st.error("Invalid API key!!! Please try again.", icon="❌")
        return

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a document (.pdf or .txt)", type=("pdf", "txt"),
        help="Supported formats: .pdf, .txt"
    )

    if uploaded_file is not None:
        if st.button("Process"):
            try:
                if uploaded_file.type == "text/plain":
                    document = uploaded_file.getvalue().decode()
                elif uploaded_file.type == "application/pdf":
                    document = read_pdf(uploaded_file)
                else:
                    st.error("Unsupported file type. Please upload a .pdf or .txt file.")
                    return

                st.session_state['document'] = document
                st.success("File processed successfully!")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                return

    # Chatbot functionality
    if not st.session_state['waiting_for_more_info']:
        question = st.chat_input("Ask a question about the document:")

        if question:
            st.chat_message("user").write(question)
            st.session_state['messages'].append({"role": "user", "content": question})

            if st.session_state['document'] is not None:
                try:
                    messages = [
                        {"role": "system", "content": f"Here's a document: {st.session_state['document']}"},
                        *st.session_state['messages']
                    ]

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        stream=True
                    )

                    message_placeholder = st.empty()
                    full_response = ""

                    for chunk in response:
                        full_response += chunk['choices'][0].get('delta', {}).get('content', '')
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    st.session_state['messages'].append({"role": "assistant", "content": full_response})

                    # Set waiting_for_more_info to True after each response
                    st.session_state['waiting_for_more_info'] = True

                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")

    # Handle the follow-up question
    if st.session_state['waiting_for_more_info']:
        more_info = st.radio("Do you want more information?", ("Yes", "No"))
        if st.button("Submit"):
            if more_info == "Yes":
                st.session_state['messages'].append({"role": "user", "content": " Please provide more information."})
                try:
                    messages = [
                        {"role": "system", "content": f"Here's a document: {st.session_state['document']}"},
                        *st.session_state['messages']
                    ]

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        stream=True
                    )

                    message_placeholder = st.empty()
                    full_response = ""

                    for chunk in response:
                        full_response += chunk['choices'][0].get('delta', {}).get('content', '')
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    st.session_state['messages'].append({"role": "assistant", "content": full_response})

                except Exception as e:
                    st.error(f"Error generating additional information: {str(e)}")
            else:
                st.write("What question do you want me to answer?")
            st.session_state['waiting_for_more_info'] = False
            try:
                st.rerun()
            except AttributeError:
                st.rerun()

    # Display conversation history
    st.subheader("Conversation History")
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if __name__ == "__main__":
    run()