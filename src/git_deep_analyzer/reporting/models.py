"""Report data models."""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ReportFormat(Enum):
    """Report format options."""
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"


class ReportDetailLevel(Enum):
    """Report detail level options."""
    CONCISE = "concise"
    """Minimal information, high-level summary only."""

    STANDARD = "standard"
    """Balanced information, key insights with moderate detail."""

    DETAILED = "detailed"
    """Comprehensive information, all insights and details."""


@dataclass
class ReportSection:
    """A section within a report."""

    title: str
    """Section title."""

    content: str
    """Section content (can be HTML, Markdown, or plain text)."""

    level: int = 1
    """Section heading level (1-6)."""

    id: Optional[str] = None
    """Optional unique identifier for the section."""

    subsections: List["ReportSection"] = field(default_factory=list)
    """Subsections nested under this section."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata for the section."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "id": self.id,
            "subsections": [s.to_dict() for s in self.subsections],
            "metadata": self.metadata
        }


@dataclass
class ReportData:
    """Complete report data."""

    title: str
    """Report title."""

    format: ReportFormat
    """Report format."""

    detail_level: ReportDetailLevel = ReportDetailLevel.STANDARD
    """Detail level for the report."""

    author: Optional[str] = None
    """Report author (optional)."""

    created_at: Optional[str] = None
    """Report creation timestamp (ISO 8601 format)."""

    sections: List[ReportSection] = field(default_factory=list)
    """Report sections in order."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata for the report."""

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "title": self.title,
            "format": self.format.value,
            "detail_level": self.detail_level.value,
            "author": self.author,
            "created_at": self.created_at,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata
        }

    def add_section(self, section: ReportSection, index: Optional[int] = None) -> None:
        """
        Add a section to the report.

        Args:
            section: Section to add
            index: Optional index to insert at (appends if None)
        """
        if index is None:
            self.sections.append(section)
        else:
            self.sections.insert(index, section)

    def get_section_by_id(self, section_id: str) -> Optional[ReportSection]:
        """
        Get section by ID (recursive).

        Args:
            section_id: Section ID to find

        Returns:
            Section if found, None otherwise
        """
        for section in self.sections:
            if section.id == section_id:
                return section
            # Search subsections recursively
            result = self._find_section_recursive(section, section_id)
            if result:
                return result
        return None

    def _find_section_recursive(
        self,
        section: ReportSection,
        section_id: str
    ) -> Optional[ReportSection]:
        """
        Recursively search for section by ID.

        Args:
            section: Current section to search
            section_id: Section ID to find

        Returns:
            Section if found, None otherwise
        """
        for subsection in section.subsections:
            if subsection.id == section_id:
                return subsection
            result = self._find_section_recursive(subsection, section_id)
            if result:
                return result
        return None
