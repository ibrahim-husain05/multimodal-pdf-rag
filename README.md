# multimodal-pdf-rag

<img width="1916" height="890" alt="Screenshot 2026-09-26 132919" src="https://github.com/user-attachments/assets/0db92166-a8c6-41d7-8246-5232c1b603b5" />








<img width="1826" height="363" alt="Screenshot 2026-09-26 133221" src="https://github.com/user-attachments/assets/d276c2e0-7dbb-4a77-9e91-be46a10a6555" />




A locally running AI-powered chatbot that allows users to upload PDF documents and ask questions about their contents, including text, images, tables, and charts.

Built using **Python, LangChain, Ollama, ChromaDB, Qwen2.5-VL, and Streamlit**.

## Features

* Drag-and-drop PDF upload with an interactive chat interface.
* Extracts text, images, and tables from PDFs.
* Uses Qwen2.5-VL to analyze visual content.
* Uses semantic search to retrieve relevant information.
* Generates context-aware answers using Llama 3.2.
* Prevents duplicate PDF processing using SHA-256 hashing.
* Runs locally without requiring paid cloud AI APIs.

## Tech Stack

| Technology          | Purpose                       |
| ------------------- | ----------------------------- |
| Python              | Backend development           |
| Streamlit           | Web interface                 |
| LangChain           | RAG pipeline                  |
| Ollama              | Local AI model execution      |
| Llama 3.2           | Answer generation             |
| Qwen2.5-VL 3B       | Image and table understanding |
| mxbai-embed-large   | Text embeddings               |
| ChromaDB            | Vector database               |
| Unstructured        | PDF content extraction        |
| Tesseract & Poppler | OCR and PDF processing        |

## How It Works

1. The user uploads a PDF through Streamlit.
2. Unstructured extracts text, images, and tables.
3. Qwen2.5-VL generates descriptions of extracted visual content.
4. The extracted content is converted into embeddings and stored in ChromaDB.
5. Relevant information is retrieved when the user asks a question.
6. Llama 3.2 generates an answer using the retrieved context. Page-specific image questions can be answered directly by Qwen2.5-VL.

## Installation

Clone the repository:

```bash
git clone https://github.com/ibrahim-husain05/multimodal-pdf-rag.git
cd multimodal-pdf-rag
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Ollama and download the required models:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
ollama pull qwen2.5vl:3b
```

Install Tesseract OCR and Poppler, and add their executable directories to your system PATH.

## Run the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser, upload a PDF, and start asking questions.

## Current Limitations

* Image questions work most reliably when the page number is specified.
* PDF processing can take time, especially for large documents.
* Model performance depends on available RAM and GPU resources.

## Future Improvements

* Automatic image and chart retrieval without specifying page numbers.
* Support for multiple PDFs in a single conversation.
* Source citations and PDF page previews.
* Improved retrieval and reranking.

## Author

**Ibrahim Husain**

Developed as a personal project to explore Retrieval-Augmented Generation (RAG), natural language processing, computer vision, and locally hosted AI models.

