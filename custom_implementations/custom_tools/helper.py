import json
import uuid
from pathlib import Path

import PyPDF2


async def count_pages_in_pdf(file_path: Path) -> int:
    """
    Count the number of pages in a PDF document
    :param file_path: Path to the PDF file
    :return: Number of pages, or 0 if error
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        print(f"Error counting pages in {file_path.name}: {e}")
        return 0


async def update_datasource_index() -> bool:
    """
    Update the data_index.json file with current PDF documents in datasource
    Uses UUID for document IDs and counts pages for each document
    :return: True if successful, False otherwise
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    datasource_path = project_root / "datasources"
    index_file_path = datasource_path / "data_index.json"

    try:
        # Check if datasource directory exists
        if not datasource_path.exists():
            print(f"Error: Datasource directory not found at {datasource_path}")
            return False

        # Get all PDF files in the datasource directory
        pdf_files = []
        for file_path in datasource_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.pdf':
                pdf_files.append(file_path)

        # Create a new index with UUIDs and page counts
        new_index = []
        existing_docs = {}

        # Load existing index to preserve IDs for existing documents
        if index_file_path.exists():
            try:
                with open(index_file_path, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
                    for doc in existing_index:
                        existing_docs[doc['doc_name']] = doc['id']
            except:
                pass

        # Process each PDF file
        for file_path in pdf_files:
            doc_name = file_path.name

            # Use existing UUID if document already exists, otherwise create new UUID
            doc_id = existing_docs.get(doc_name, str(uuid.uuid4()))

            # Count pages in the PDF
            num_pages = await count_pages_in_pdf(file_path)

            new_index.append({
                'id': doc_id,
                'doc_name': doc_name,
                'num_pages': num_pages
            })

        # Sort by document name for consistency
        new_index.sort(key=lambda x: x['doc_name'])

        # Write to data_index.json
        with open(index_file_path, 'w', encoding='utf-8') as f:
            json.dump(new_index, f, indent=2, ensure_ascii=False)

        print(f"Successfully updated index with {len(new_index)} documents")
        return True

    except Exception as e:
        print(f"Error updating datasource index: {e}")
        return False