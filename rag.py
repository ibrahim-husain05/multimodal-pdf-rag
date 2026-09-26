
import hashlib
import re
from pathlib import Path

from ollama import chat
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage

from pdf_processor import process_pdf


DB_PATH = "db/chroma_db"
IMAGE_DIR = "extracted_images"

embeddings = OllamaEmbeddings(model="mxbai-embed-large")


def get_pdf_id(pdf_path):
    """Generate a unique ID for each PDF."""

    sha256 = hashlib.sha256()

    with open(pdf_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def get_db():
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )


def get_page_images(pdf_id, page):
    """Return image records extracted from the requested PDF page."""
    records = get_db().get(
        where={
            "$and": [
                {"pdf_id": pdf_id},
                {"type": "image"}
            ]
        },
        include=["metadatas"]
    )

    metadatas = [
        metadata for metadata in records.get("metadatas", [])
        if metadata.get("page") == page
    ]

    return {
        "ids": [str(index) for index in range(len(metadatas))],
        "metadatas": metadatas
    }


# Analyze an extracted image or table using Qwen.
def analyze_image(image_path):

    response = chat(
        model="qwen2.5vl:3b",
        messages=[
            {
                "role": "user",
                "content": (
                    "Describe this image accurately. "
                    "If it contains a chart, explain its labels, "
                    "values and trends. If it contains a table, "
                    "extract its contents. "
                    "Do not invent unreadable information."
                ),
                "images": [str(Path(image_path).resolve())]
            }
        ]
    )

    return response.message.content or ""


# Ingestion
def ingest_pdf(pdf_path):

    pdf_id = get_pdf_id(pdf_path)
    db = get_db()

    existing = db.get(
        where={"pdf_id": pdf_id},
        limit=1,
        include=[]
    )

    if existing["ids"]:
        print("PDF already exists. Skipping ingestion.")
        return db

    # Use a separate directory for each PDF.
    image_dir = Path(IMAGE_DIR) / pdf_id
    image_dir.mkdir(parents=True, exist_ok=True)

    # Process PDF text and extract its images.
    chunks = process_pdf(
        pdf_path,
        output_dir=str(image_dir)
    )

    texts = []
    metadatas = []
    ids = []

    # Store text chunks.
    for index, chunk in enumerate(chunks):

        text = chunk["text"].strip()

        if not text:
            continue

        texts.append(text)

        metadatas.append({
            "pdf_id": pdf_id,
            "source": Path(pdf_path).name,
            "page": chunk["page_number"] or 0,
            "type": "text"
        })

        ids.append(f"{pdf_id}_text_{index}")

    # Analyze extracted images and tables.
    image_files = sorted(
        file for file in image_dir.iterdir()
        if file.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    for index, image_path in enumerate(image_files):

        print(f"Analyzing: {image_path.name}")

        description = analyze_image(image_path)

        if not description.strip():
            continue

        # Extract page number from Unstructured's filename.
        # Examples: figure-2-1.jpg, table-3-1.jpg
        parts = image_path.stem.split("-")

        try:
            page = int(parts[1])
        except (IndexError, ValueError):
            page = 0

        texts.append(description)

        metadatas.append({
            "pdf_id": pdf_id,
            "source": Path(pdf_path).name,
            "page": page,
            "type": "image",
            "image_path": str(image_path.resolve())
        })

        ids.append(f"{pdf_id}_image_{index}")

    # Store everything in small batches.
    for i in range(0, len(texts), 32):

        db.add_texts(
            texts=texts[i:i + 32],
            metadatas=metadatas[i:i + 32],
            ids=ids[i:i + 32]
        )

    print(f"Stored {len(texts)} text/image records.")

    return db


# Retrieval
def retrieve(question, pdf_id=None):

    db = get_db()

    search_filter = (
        {"pdf_id": pdf_id} if pdf_id else None
    )

    return db.similarity_search(
        question,
        k=5,
        filter=search_filter
    )


# Answer generation
def ask_question(question, pdf_id=None):
    match = re.search(r"page\s+(\d+)", question.lower())

    if pdf_id and match and any(
        word in question.lower()
        for word in ["image", "figure", "chart", "diagram", "table"]
    ):
        page = int(match.group(1))
        images = get_page_images(pdf_id, page)

        if images["ids"]:
            answers = []

            for metadata in images["metadatas"]:
                response = chat(
                    model="qwen2.5vl:3b",
                    messages=[{
                        "role": "user",
                        "content": question,
                        "images": [metadata["image_path"]]
                    }]
                )
                answers.append(response.message.content)

            return "\n\n".join(answers)


    docs = retrieve(question, pdf_id)

    if not docs:
        return "No relevant information found."

    context = "\n\n".join(
        f"Page {doc.metadata.get('page', '?')} "
        f"({doc.metadata.get('type', 'text')}):\n"
        f"{doc.page_content}"
        for doc in docs
    )

    llm = ChatOllama(
        model="llama3.2",
        temperature=0
    )

    response = llm.invoke([
        SystemMessage(
            content=(
            "You are a PDF question-answering assistant. "
        "The provided context contains extracted PDF text and "
        "image descriptions generated by a vision model. "
        "Use those descriptions to answer questions about "
        "images, charts, figures and tables. "
        "Do not say you cannot view images when an image "
        "description is available. "
        "If the relevant information is missing, say so. "
        "Mention page numbers when available.")
        ),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion: {question}"
        )
    ])

    return response.content


if __name__ == "__main__":

    pdf_path = "Full Stack Internship Training Report (1).pdf"  # Replace with your PDF file path

    ingest_pdf(pdf_path)

    pdf_id = get_pdf_id(pdf_path)
    db = get_db()



    while True:

        question = input("\nAsk a question (or 'exit'): ")

        if question.lower() == "exit":
            break

        answer = ask_question(question, pdf_id)

        print("\nAnswer:", answer)