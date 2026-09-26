# pdf_processor.py

import os
from collections import Counter
from pathlib import Path
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Tesseract-OCR"

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

def process_pdf(pdf_path, output_dir="extracted_images"):
    """
    Process a PDF and return structured chunks.

    Extracts:
    - Text
    - Titles
    - Tables
    - Images
    - Page numbers

    Returns:
        list: Processed document chunks
    """

    os.makedirs(output_dir, exist_ok=True)

    print(f"Processing PDF: {pdf_path}")

    # ---------------------------------------------------------
    # 1. Partition PDF into structured elements
    # ---------------------------------------------------------

    elements = partition_pdf(
        filename=pdf_path,

        # hi_res is useful for PDFs containing tables/images
        strategy="hi_res",

        # Detect table structure
        infer_table_structure=True,

        # Extract images and tables from the PDF
        extract_image_block_types=["Image", "Table"],

        # Save extracted image data as files
        extract_image_block_to_payload=False,

        # Directory where extracted images will be stored
        extract_image_block_output_dir=output_dir,
    )

    for element in elements:
        element_type = type(element).__name__

        if element_type in ["Image", "Table"]:
            metadata = element.metadata

            print(f"\nType: {element_type}")
            print(f"Page: {metadata.page_number}")
            print(f"Image path: {getattr(metadata, 'image_path', None)}")
            print(f"Has image data: {bool(getattr(metadata, 'image_base64', None))}")

            if element_type == "Table":
                print(f"HTML: {getattr(metadata, 'text_as_html', None)}")

    print(f"Extracted {len(elements)} elements")

    # ---------------------------------------------------------
    # 2. Chunk the extracted elements
    # ---------------------------------------------------------
    print("\nExtracted element types:")
    print(Counter(type(e).__name__ for e in elements))

    for element in elements:
        if type(element).__name__ in ["Image", "Table"]:
            print(
                type(element).__name__,
                "Page:",
                element.metadata.page_number
            )

    chunks = chunk_by_title(
        elements,

        # Maximum size of a chunk
        max_characters=1500,

        # Try to create a new chunk around this size
        new_after_n_chars=1200,

        # Keep some previous content for context
        overlap=150,

        # Don't allow very small isolated chunks
        combine_text_under_n_chars=300,
    )

    print(f"Created {len(chunks)} chunks")

    # ---------------------------------------------------------
    # 3. Convert chunks into dictionaries
    # ---------------------------------------------------------

    processed_chunks = []

    for index, chunk in enumerate(chunks):

        # Extract text
        text = str(chunk)

        # Metadata provided by Unstructured
        metadata = chunk.metadata.to_dict()

        page_number = metadata.get("page_number")
        filename = metadata.get("filename")

        # Element type
        element_type = type(chunk).__name__

        processed_chunks.append(
            {
                "id": index,
                "text": text,
                "element_type": element_type,
                "page_number": page_number,
                "filename": filename,
                "metadata": metadata,
            }
        )

    return processed_chunks


# -------------------------------------------------------------
# Test the processor directly
# -------------------------------------------------------------

if __name__ == "__main__":

    pdf_path = "Full Stack Internship Training Report (1).pdf"  # Replace with your PDF file path

    chunks = process_pdf(pdf_path)

    print("\n" + "=" * 60)
    print("PDF PROCESSING COMPLETE")
    print("=" * 60)

    for chunk in chunks[:5]:

        print("\nChunk ID:", chunk["id"])
        print("Type:", chunk["element_type"])
        print("Page:", chunk["page_number"])

        print("Text:")
        print(chunk["text"][:500])

        print("-" * 60)