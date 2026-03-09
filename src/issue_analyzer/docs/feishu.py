"""Feishu document client."""

import requests
from typing import List, Optional
from issue_analyzer.models import Document, DocumentType
from .base import DocClient


class FeishuClient(DocClient):
    """Feishu document client implementation."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        app_id: Optional[str] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.app_id = app_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    @property
    def repository(self) -> str:
        """Get repository identifier."""
        return "feishu"

    def get_documents(
        self,
        issue: str,
        doc_types: Optional[List[str]] = None
    ) -> List[Document]:
        """Get documents related to an issue."""
        # Feishu document search
        search_url = f"{self.base_url}/openapis/docx/v1/search"

        # Search for documents with issue in title
        query = f"{issue}"

        documents: List[Document] = []

        try:
            response = self.session.post(search_url, json={
                "query": query,
                "size": 100
            })

            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    for item in data["data"]["items"]:
                        doc = self._parse_document(item, issue_id)
                        if doc:
                            documents.append(doc)

        except Exception:
            pass

        return documents

    def get_document_content(self, doc_id: str) -> str:
        """Get full content of a document."""
        doc_url = f"{self.base_url}/openapis/docx/v1/documents/{doc_id}/blocks"

        try:
            response = self.session.get(doc_url)
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    blocks = data["data"]
                    # Extract text from blocks
                    text_blocks = []
                    for block in blocks:
                        if "children" in block:
                            for child in block["children"]:
                                if "text" in child:
                                    text_blocks.append(child["text"]["elements"][0]["text_run"]["content"])

                    return "\n".join(text_blocks)

        except Exception:
            pass

        return ""

    def _parse_document(self, item: dict, issue_id: str) -> Optional[Document]:
        """Parse Feishu search result to Document model."""
        try:
            title = item.get("title", "")
            doc_id = item.get("document", {}).get("document_id", "")

            doc_type = DocumentType.CUSTOM

            # Try to determine doc type from title
            if "requirement" in title.lower():
                doc_type = DocumentType.REQUIREMENTS
            elif "design" in title.lower():
                doc_type = DocumentType.DESIGN

            return Document(
                id=doc_id,
                type=doc_type,
                title=title,
                content="",  # Will be fetched on demand
                issue_id=issue_id,
                url=f"{self.base_url}/docx/{doc_id}",
                source="feishu"
            )
        except Exception:
            return None
