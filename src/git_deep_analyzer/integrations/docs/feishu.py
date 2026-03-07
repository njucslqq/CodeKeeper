"""Feishu docs system integration."""

import requests
from typing import List, Optional
from datetime import datetime
from .base import DocsSystemBase
from .models import Document, DocumentType


class FeishuDocs(DocsSystemBase):
    """Feishu docs system integration."""

    def __init__(self, config: dict):
        """
        Initialize Feishu docs.

        Args:
            config: Configuration dict with api_base, user_access_token, app_id
        """
        super().__init__(config)
        self.api_base = config.get("api_base", "https://open.feishu.cn/open-apis")
        self.user_access_token = config.get("user_access_token", "")
        self.app_id = config.get("app_id", "")
        self.session = None

    def connect(self) -> bool:
        """Connect to Feishu API."""
        import os

        self.session = requests.Session()

        # Support multiple authentication methods
        if self.user_access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.user_access_token}",
                "Content-Type": "application/json; charset=utf-8"
            })
        elif os.environ.get("FEISHU_USER_ACCESS_TOKEN"):
            token = os.environ["FEISHU_USER_ACCESS_TOKEN"]
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            })

        # Test connection
        try:
            response = self.session.get(
                f"{self.api_base}/contact/v3/users/me",
                timeout=30
            )
            return response.status_code == 200
        except Exception:
            return False

    def fetch_documents(
        self,
        space_id: str,
        doc_type: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        page_token: Optional[str] = None
    ) -> List[Document]:
        """
        Fetch documents from Feishu space.

        Args:
            space_id: Space ID
            doc_type: Filter by doc type (doc/sheet/wiki/docx)
            since: Start date filter
            until: End date filter
            page_token: Pagination token

        Returns:
            List of documents
        """
        if not self.session:
            raise RuntimeError("Not connected to Feishu API")

        url = f"{self.api_base}/docx/v1/documents/search"

        # Build request body
        body = {
            "query": f'space_id = "{space_id}"'
        }

        if doc_type:
            body["query"] += f' and doc_type = "{doc_type}"'

        if since:
            body["query"] += f' and create_time >= {int(since.timestamp() * 1000)}'

        if until:
            body["query"] += f' and create_time <= {int(until.timestamp() * 1000)}'

        if page_token:
            body["page_token"] = page_token

        body["page_size"] = 50

        response = self.session.post(url, json=body, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Feishu API error: {response.text}")

        data = response.json()

        documents = []
        for item in data.get("data", {}).get("items", []):
            doc = self._parse_document(item)
            documents.append(doc)

        return documents

    def fetch_document_detail(self, document_id: str) -> Document:
        """
        Fetch document detail with content blocks.

        Args:
            document_id: Document ID (node_token)

        Returns:
            Document with content
        """
        if not self.session:
            raise RuntimeError("Not connected to Feishu API")

        url = f"{self.api_base}/docx/v1/documents/{document_id}"

        response = self.session.get(url, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Feishu API error: {response.text}")

        data = response.json()

        return self._parse_document_detail(data.get("data", {}))

    def _parse_document(self, item: dict) -> Document:
        """
        Parse document item from Feishu API.

        Args:
            item: Document item from API

        Returns:
            Document object
        """
        node_token = item.get("node_token", "")
        title = item.get("title", "")
        doc_type = item.get("type", "doc")

        # Map Feishu type to DocumentType
        if doc_type == "doc":
            document_type = DocumentType.OTHER
        elif doc_type == "sheet":
            document_type = DocumentType.SPEC
        elif doc_type == "wiki":
            document_type = DocumentType.REQUIREMENT
        elif doc_type == "docx":
            document_type = DocumentType.DESIGN
        else:
            document_type = DocumentType.OTHER

        # Parse timestamps
        create_time = item.get("create_time", 0)
        update_time = item.get("update_time", 0)

        created_at = datetime.fromtimestamp(create_time / 1000) if create_time else None
        updated_at = datetime.fromtimestamp(update_time / 1000) if update_time else None

        return Document(
            id=node_token,
            title=title,
            content="",  # Content loaded separately
            type=document_type,
            created_at=created_at,
            updated_at=updated_at,
            author=item.get("creator", {}).get("open_id", ""),
            author_email="",
            space_id=item.get("space_id", ""),
            url=f"https://feishu.cn/docx/{node_token}"
        )

    def _parse_document_detail(self, data: dict) -> Document:
        """
        Parse document detail with blocks.

        Args:
            data: Document detail from API

        Returns:
            Document with content
        """
        document = data.get("document", {})
        node_token = data.get("node_token", "")
        title = document.get("title", "")
        doc_type = document.get("type", "doc")

        # Map Feishu type
        if doc_type == "doc":
            document_type = DocumentType.OTHER
        elif doc_type == "sheet":
            document_type = DocumentType.SPEC
        elif doc_type == "wiki":
            document_type = DocumentType.REQUIREMENT
        elif doc_type == "docx":
            document_type = DocumentType.DESIGN
        else:
            document_type = DocumentType.OTHER

        # Extract content from blocks
        blocks = document.get("blocks", [])
        content = self._extract_text_from_blocks(blocks)

        # Parse timestamps
        create_time = document.get("create_time", 0)
        update_time = document.get("update_time", 0)

        created_at = datetime.fromtimestamp(create_time / 1000) if create_time else None
        updated_at = datetime.fromtimestamp(update_time / 1000) if update_time else None

        return Document(
            id=node_token,
            title=title,
            content=content,
            type=document_type,
            created_at=created_at,
            updated_at=updated_at,
            author=document.get("creator", {}).get("open_id", ""),
            author_email="",
            space_id=document.get("space_id", ""),
            url=f"https://feishu.cn/docx/{node_token}"
        )

    def _extract_text_from_blocks(self, blocks: List[dict]) -> dict:
        """
        Extract text content from document blocks.

        Args:
            blocks: List of content blocks

        Returns:
            Content dictionary with text and structure
        """
        content = {
            "text": "",
            "blocks": []
        }

        for block in blocks:
            block_data = self._extract_block_content(block)
            content["blocks"].append(block_data)

            # Extract text from text_run elements
            if block.get("block_type") == 1:  # text block
                text_run = block.get("text", {})
                elements = text_run.get("elements", [])
                for element in elements:
                    if element.get("type") == 1:  # text_run element
                        text_run_data = element.get("text_run", {})
                        content_text = text_run_data.get("content", "")
                        content["text"] += content_text

        return content

    def _extract_block_content(self, block: dict) -> dict:
        """
        Extract block content.

        Args:
            block: Block data

        Returns:
            Block dictionary
        """
        return {
            "block_id": block.get("block_id", ""),
            "block_type": block.get("block_type", ""),
            "content": str(block.get("text", {}))
        }
