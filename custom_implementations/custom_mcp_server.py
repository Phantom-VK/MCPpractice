from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import List, Optional

from custom_implementations.custom_tools.models import Document
from custom_implementations.custom_tools.tools import (
    get_document_list as get_document_list_service,
    read_document_content as read_document_content_service,
    read_document_page as read_document_page_service,
)

load_dotenv()

mcp = FastMCP("documents_server")


@mcp.tool()
async def get_document_list() -> List[Document]:
    """
    Update the datasource index and return the list of available documents.
    :return: List of Document objects with id, doc_name, and num_pages
    """
    return await get_document_list_service()


@mcp.tool()
async def read_document_content(doc_name: Optional[str] = None, doc_id: Optional[str] = None) -> Optional[str]:
    """
    Read and return a document's content. Either doc_name or doc_id must be provided.
    :param doc_name: Name of the document to read (optional if doc_id provided)
    :param doc_id: ID of the document to read (optional if doc_name provided)
    :return: Document content as text, or None if error
    """
    return await read_document_content_service(doc_name=doc_name, doc_id=doc_id)


@mcp.tool()
async def read_document_page(
    doc_name: Optional[str] = None,
    doc_id: Optional[str] = None,
    page_number: int = 1,
) -> Optional[str]:
    """
    Read and return a specific page content from a document. Either doc_name or doc_id must be provided.
    :param doc_name: Name of the document to read (optional if doc_id provided)
    :param doc_id: ID of the document to read (optional if doc_name provided)
    :param page_number: Page number to read (1-indexed, defaults to 1)
    :return: Document page content as text, or None if error
    """
    return await read_document_page_service(doc_name=doc_name, doc_id=doc_id, page_number=page_number)


if __name__ == "__main__":
    mcp.run(transport='stdio')
