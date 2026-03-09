"""Document name parser with registry."""

import re
from typing import Optional, Callable, Dict
from abc import ABC, abstractmethod


class DocNameParser(ABC):
    """Abstract document name parser."""

    @abstractmethod
    def parse(self, doc_name: str, pattern: str) -> Optional[str]:
        """Parse issue ID from document name.

        Args:
            doc_name: Document name
            pattern: Naming pattern (e.g., "{issue_id}-*")

        Returns:
            Issue ID if matched, None otherwise
        """
        pass


class DocNameParserRegistry:
    """Registry for document name parsers."""

    _parsers: Dict[str, Callable[[str, str], Optional[str]]] = {}

    @classmethod
    def register(cls, name: str, parser: Callable[[str, str], Optional[str]]):
        """Register a document name parser.

        Args:
            name: Parser name
            parser: Parser function
        """
        cls._parsers[name] = parser

    @classmethod
    def parse(
        cls,
        doc_name: str,
        pattern: str,
        parser: Optional[str] = "default"
    ) -> Optional[str]:
        """Parse document name using specified parser.

        Args:
            doc_name: Document name
            pattern: Naming pattern
            parser: Parser name to use (default, confluence, feishu)

        Returns:
            Issue ID if matched, None otherwise
        """
        if parser and parser in cls._parsers:
            return cls._parsers[parser](doc_name, pattern)

        # Try default parser
        if "default" in cls._parsers:
            return cls._parsers["default"](doc_name, pattern)

        return None


# Built-in parsers


def _parse_default_issue_id(doc_name: str, pattern: str) -> Optional[str]:
    """Parse issue ID from document name using pattern matching.

    Args:
        doc_name: Document name
        pattern: Naming pattern (e.g., "{issue_id}-*")

    Returns:
        Issue ID if matched, None otherwise
    """
    # Convert pattern to regex
    # {issue_id}-* -> (?P<issue_id>-).*
    regex_pattern = pattern.replace("{issue_id}", r"(?P<[^>]+>)")
    regex_pattern = regex_pattern.replace("*", ".*")

    match = re.match(regex_pattern, doc_name, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def _parse_confluence_issue_id(doc_name: str, pattern: str) -> Optional[str]:
    """Parse issue ID from Confluence document title.

    Confluence often uses format like "PROJ-123 - Feature Description"

    Args:
        doc_name: Document name
        pattern: Naming pattern (not used for Confluence)

    Returns:
        Issue ID if matched, None otherwise
    """
    # Common Confluence patterns
    patterns = [
        r'^([A-Z]+-\d+)',  # PROJ-123
        r'^([A-Z]+-\d+)',  # PROJ-123 (case insensitive)
    ]

    for pattern in patterns:
        match = re.match(pattern, doc_name.strip())
        if match:
            return match.group(1)

    return None


def _parse_feishu_issue_id(doc_name: str, pattern: str) -> Optional[str]:
    """Parse issue ID from Feishu document title.

    Args:
        doc_name: Document name
        pattern: Naming pattern (not used for Feishu)

    Returns:
        Issue ID if matched, None otherwise
    """
    # Feishu often uses format like "PROJ-123需求文档"
    patterns = [
        r'^([A-Z]+-\d+)',  # PROJ-123
    ]

    for pattern in patterns:
        match = re.match(pattern, doc_name.strip())
        if match:
            return match.group(1)

    return None


# Register built-in parsers
DocNameParserRegistry.register("default", _parse_default_issue_id)
DocNameParserRegistry.register("confluence", _parse_confluence_issue_id)
DocNameParserRegistry.register("feishu", _parse_feishu_issue_id)


def register_doc_parser(name: str, parser: Callable[[str, str], Optional[str]]):
    """Register a custom document name parser."""
    DocNameParserRegistry.register(name, parser)


def parse_doc_name(doc_name: str, pattern: str, parser: Optional[str] = None) -> Optional[str]:
    """Parse issue ID from document name.

    Args:
        doc_name: Document name
        pattern: Naming pattern
        parser: Parser name to use

    Returns:
        Issue ID if matched, None otherwise
    """
    return DocNameParserRegistry.parse(doc_name, pattern, parser)
