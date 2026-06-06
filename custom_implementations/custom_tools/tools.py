import json
from pathlib import Path
from typing import List, Optional

import PyPDF2

from custom_implementations.custom_tools.helper import update_datasource_index
from custom_implementations.custom_tools.models import Document


async def get_document_list() -> List[Document]:
    """
    Update the datasource index and return the list of available documents
    :return: List of Document objects with id, doc_name, and num_pages
    """
    # First update the index
    update_success = await update_datasource_index()

    if not update_success:
        print("Warning: Failed to update datasource index")

    # Then return the available documents
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    index_file_path = project_root / "datasources" / "data_index.json"

    documents = []

    try:
        if not index_file_path.exists():
            print(f"Error: data_index.json not found at {index_file_path}")
            return documents

        with open(index_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            documents.append(Document(
                id=item.get('id', ''),
                doc_name=item.get('doc_name', ''),
                num_pages=item.get('num_pages', 0)
            ))

        return documents

    except Exception as e:
        print(f"Error reading documents: {e}")
        return documents

async def read_document_content(doc_name: Optional[str] = None, doc_id: Optional[str] = None) -> Optional[str]:
    """
    Read and returns document's content. Either doc_name or doc_id must be provided.
    :param doc_name: Name of the document to read (optional if doc_id provided)
    :param doc_id: ID of the document to read (optional if doc_name provided)
    :return: Document content as text, or None if error
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    datasource_path = project_root / "datasources"
    index_file_path = datasource_path / "data_index.json"

    # Validate that at least one identifier is provided
    if not doc_name and not doc_id:
        print("Error: Either doc_name or doc_id must be provided")
        return None

    try:
        # If doc_id is provided but not doc_name, look up from index
        if doc_id and not doc_name:
            if not index_file_path.exists():
                print(f"Error: data_index.json not found at {index_file_path}")
                return None

            with open(index_file_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Search for document with matching ID
            doc_found = None
            for doc in index_data:
                if doc.get('id') == doc_id:
                    doc_found = doc
                    break

            if not doc_found:
                print(f"Error: No document found with ID: {doc_id}")
                return None

            doc_name = doc_found.get('doc_name')
            if not doc_name:
                print(f"Error: Document with ID {doc_id} has no name")
                return None

        # If doc_name was provided directly or found via ID, proceed
        file_path = datasource_path / doc_name

        # Check if file exists
        if not file_path.exists():
            print(f"Error: Document not found at {file_path}")
            return None

        # Check if it's a PDF file
        if file_path.suffix.lower() != '.pdf':
            print(f"Error: {doc_name} is not a PDF file")
            return None

        # Extract text from PDF
        text_content = []

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add if there's actual text
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")
                else:
                    text_content.append(f"--- Page {page_num} ---\n[No extractable text on this page]")

        if not text_content:
            return f"[No text content could be extracted from {doc_name}]"

        # Combine all pages
        full_text = "\n\n".join(text_content)

        # Add document header
        header = f"Document: {doc_name}\nTotal Pages: {len(pdf_reader.pages)}\n{'-' * 50}\n\n"

        return header + full_text

    except Exception as e:
        print(f"Error reading document {doc_name or doc_id}: {e}")
        return None

async def read_document_page(doc_name: Optional[str] = None, doc_id: Optional[str] = None, page_number: int = 1) -> Optional[str]:
    """
    Read and returns a specific page content from a document. Either doc_name or doc_id must be provided.
    :param doc_name: Name of the document to read (optional if doc_id provided)
    :param doc_id: ID of the document to read (optional if doc_name provided)
    :param page_number: Page number to read (1-indexed, defaults to 1)
    :return: Document page content as text, or None if error
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    datasource_path = project_root / "datasources"
    index_file_path = datasource_path / "data_index.json"

    # Validate that at least one identifier is provided
    if not doc_name and not doc_id:
        print("Error: Either doc_name or doc_id must be provided")
        return None

    # Validate page number
    if page_number < 1:
        print("Error: Page number must be 1 or greater")
        return None

    try:
        # If doc_id is provided but not doc_name, look up from index
        if doc_id and not doc_name:
            if not index_file_path.exists():
                print(f"Error: data_index.json not found at {index_file_path}")
                return None

            with open(index_file_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Search for document with matching ID
            doc_found = None
            for doc in index_data:
                if doc.get('id') == doc_id:
                    doc_found = doc
                    break

            if not doc_found:
                print(f"Error: No document found with ID: {doc_id}")
                return None

            doc_name = doc_found.get('doc_name')
            if not doc_name:
                print(f"Error: Document with ID {doc_id} has no name")
                return None

        # If doc_name was provided directly or found via ID, proceed
        file_path = datasource_path / doc_name

        # Check if file exists
        if not file_path.exists():
            print(f"Error: Document not found at {file_path}")
            return None

        # Check if it's a PDF file
        if file_path.suffix.lower() != '.pdf':
            print(f"Error: {doc_name} is not a PDF file")
            return None

        # Extract the specific page from PDF
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            # Validate page number is within range
            if page_number > total_pages:
                print(f"Error: Page number {page_number} exceeds total pages ({total_pages}) in {doc_name}")
                return None

            # Extract the specific page (0-indexed in PyPDF2)
            page = pdf_reader.pages[page_number - 1]
            page_text = page.extract_text()

            # Prepare the response
            header = f"Document: {doc_name}\nPage: {page_number} of {total_pages}\n{'-' * 50}\n\n"

            if not page_text or not page_text.strip():
                content = f"[No extractable text found on page {page_number}]"
            else:
                content = page_text

            return header + content

    except Exception as e:
        print(f"Error reading page {page_number} from document {doc_name or doc_id}: {e}")
        return None


# if __name__ == '__main__':
#     print(asyncio.run(get_document_list()))
#     # print(asyncio.run(read_document_page(doc_id = 6, page_number = 3)))
