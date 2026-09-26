
import streamlit as st
from pathlib import Path
from rag import ingest_pdf, ask_question, get_pdf_id

st.set_page_config(
    page_title="Multimodal PDF Chatbot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Multimodal PDF Chatbot")
st.caption("Chat with PDF text, images, charts and tables using local AI.")

UPLOAD_DIR = Path("documents")
UPLOAD_DIR.mkdir(exist_ok=True)


uploaded_file = st.file_uploader(
    "Drag and drop your PDF here",
    type=["pdf"]
)

if uploaded_file:

    pdf_path = UPLOAD_DIR / uploaded_file.name
    pdf_path.write_bytes(uploaded_file.getbuffer())

    pdf_id = get_pdf_id(pdf_path)

    # Process only when the selected PDF changes
    if st.session_state.get("pdf_id") != pdf_id:

        with st.spinner("Processing PDF and analyzing images..."):
            ingest_pdf(str(pdf_path))

        st.session_state.pdf_id = pdf_id
        st.session_state.messages = []

    st.success(f"Ready: {uploaded_file.name}")

    # Display previous messages
    for message in st.session_state.get("messages", []):

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    question = st.chat_input("Ask anything about your PDF...")

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):
                answer = ask_question(question, pdf_id)

            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

else:
    st.info("Upload a PDF to start chatting.")