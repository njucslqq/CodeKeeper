"""Confluence document client."""

import requests
from typing import List, Optional
from issue_analyzer.models import Document, DocumentType
from .base import DocClient


class ConfluenceClient(DocClient):
    """Confluence document client implementation."""

    def __init__(
        self,
        base_url: str,
        api_token: str,
        email: Optional[str] = None,
        space_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.email = email
        self.space_key = space_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json"
        })

    @property
    def repository(self) -> str:
        """Get repository identifier."""
        return "confluence"

    def get_documents(
        self,
        issue_id: str,
        doc_types: Optional[List[str]] = None
    ) -> List[Document]:
        """Get documents related to an issue."""
        # Search for pages by title containing issue ID
        search_url = f"{self.base_url}/rest/api/content/search"
        params = {
            "cql": f'title ~ "{issue_id}"',
            "limit": 100
        }

        if self.space_key:
            params["cql"] = f'spaceKey = {self.space_key} and title ~ "{issue_id}"'

        documents: List[Document] = []

        try:
            response = self.session.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    for result in data["results"]:
                        doc = self._parse_document(result, issue_id)
                        if doc:
                            documents.append(doc)

        except Exception:
            pass

        return documents

    def get_document_content(self, page_id: str) -> str:
        """Get full content of a document."""
        url = f"{self.base_url}/rest/api/content/{page_id}?expand=body.storage.view"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                if "body" in data:
                    storage = data["body"].get("storage", {})
                    if "value" in storage:
                        return storage["value"]
        except Exception:
            pass

        return ""

    def _parse_document(self, result: dict, issue_id: str) -> Optional[Document]:
        """Parse Confluence search result to Document model."""
        try:
            content = result.get("content", {})

            doc_type = DocumentType.CUSTOM
            title = content.get("title", "")

            # Try to determine doc type from title
            if "requirement" in title.lower():
                doc_type = DocumentType.REQUIREMENTS
            elif "design" in title.lower():
                doc_type = DocumentType.DESIGN

            return Document(
                id=result.get("id", ""),
                type=doc_type,
                title=title,
                content="",  # Will be fetched on demand
                issue_id=issue_id,
                url=self.base_url + content.get("_links", {}).get("webui", ""),
                source="confluence"
            )
        except Exception:
            return None

    def get_raw_page(self, page_id: str) -> Optional[dict]:
        """Get raw page data from Confluence."""
        url = f"{self.base_url}/rest/api/content/{page_id}"
        response = self.session.get(url)

        if response.status_code == 200:
            return response.json()

        return None