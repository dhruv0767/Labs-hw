import streamlit as st
from openai import OpenAI
import pypdf2


# Show title and description.
st.title("📄 Dhruv's question answering Chatbot")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

def read_pdf(uploaded_file):
  pdf_reader = PyPDF2.PdfReader(uploaded_file)
  num_pages = len(pdf_reader.pages)
  text = ""
  for page_num in range(num_pages):
      page = pdf_reader.pages[page_num]
      text += page.extract_text()
  return text

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    try:
        # Make a simple API call to validate the key.
        client.models.list()
        st.success("API key is valid!", icon="✅")
    except:
        st.error("Invalid API key!!! Please try again.", icon="❌")
    else:
        # Let the user upload a file via `st.file_uploader`.
        uploaded_file = st.file_uploader(
          "Upload a document (.pdf or .txt)", type=("pdf", "txt"),
          accept_multiple_files=False,
          help="Supported formats: .pdf, .txt"
        )


        # if an incorrect file is uploaded, clear it from memory
        if uploaded_file is not None:
          if uploaded_file.type not in ("text/plain", "application/pdf"):
            st.session_state['file_upload_warning'] = "Unsupported file type. Please upload a .pdf or .txt file."
            uploaded_file = None

          elif st.button(("Process"), disabled = not uploaded_file):
            try:
              if uploaded_file.type == "text/plain":
                st.session_state['document'] = uploaded_file.read().decode()
              elif uploaded_file.type == "application/pdf":
                st.session_state['document'] = read_pdf(uploaded_file)
              # print("Document after processing: ", document)
              st.success("File processed successfully!")
            except:
              st.error("Error processing file. Please try again.")


          # Ask the user for a question via `st.text_area`.
          question = st.text_area(
              "Now ask a question about the document!",
              placeholder="Can you give me a short summary?",
              disabled=not uploaded_file,
          )

          if 'document' in st.session_state and question:
            try:
              messages = [
                  {
                      "role": "user",
                      "content": f"Here's a document: {st.session_state['document']} \n\n---\n\n {question}",
                  }
              ]

              # Generate an answer using the OpenAI API.
              answer = client.chat.completions.create(
                  model="gpt-4o-mini",
                  messages=messages,
                  stream=True
              )

              # Stream the response to the app using `st.write_stream`.
              st.write(answer)

            except:
              st.error("Error generating answer. Please try again.")