"""Base document client interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from issue_analyzer.models import Document


class DocClient(ABC):
    """Abstract base class for document clients."""

    @abstractmethod
    def get_documents(
        self,
        issue_id: str,
        doc_types: Optional[List[str]] = None
    ) -> List[Document]:
        """Get documents related to an issue."""
        pass


class DocCollector:
    """Collect documents from configured document systems."""

    def __init__(self, clients: List[DocClient]):
        self.clients = clients

    def collect_documents(
        self,
        issue_id: str,
        doc_types: Optional[List[str]] = None
    ) -> List[Document]:
        """Collect documents from all configured systems."""
        all_docs = [Document]
        for client in self.clients:
            docs = client.get_documents(issue_id, doc_types)
            all_docs.extend(docs)
        return all_docs
