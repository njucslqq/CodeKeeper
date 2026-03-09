"""Commit message parser with registry."""

import re
from typing import Optional, Callable, Dict, Any
from abc import ABC, abstractmethod


class CommitParser(ABC):
    """Abstract commit message parser."""

    @abstractmethod
    def parse(self, message: str) -> Optional[str]:
        """Parse issue ID from commit message.

        Returns:
            Issue ID if found, None otherwise
        """
        pass


class CommitParserRegistry:
    """Registry for commit message parsers."""

    _parsers: Dict[str, Callable[[str], Optional[str]]] = {}

    @classmethod
    def register(cls, name: str, parser: Callable[[str], Optional[str]]):
        """Register a commit message parser.

        Args:
            name: Parser name
            parser: Parser function
        """
        cls._parsers[name] = parser

    @classmethod
    def parse(
        cls,
        message: str,
        parser: Optional[str] = "github"
    ) -> Optional[str]:
        """Parse commit message using specified parser.

        Args:
            message: Commit message
            parser: Parser name to use (github, gitlab, generic)

        Returns:
            Issue ID if found, None otherwise
        """
        if parser and parser in cls._parsers:
            return cls._parsers[parser](message)

        # Try all parsers
        for name, parser_func in cls._parsers.items():
            result = parser_func(message)
            if result:
                return result

        return None


# Built-in parsers


def _parse_github_issue_id(message: str) -> Optional[str]:
    """Parse GitHub-style issue ID."""
    patterns = [
        r'(?:fixes|fix|closes|closed|refs|references|ref|resolve|resolves)\s+#(\d+)',
        r'#(\d+)',
        r'([A-Z0-9]+-\d+)',  # Issue keys like PROJ-123
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _parse_gitlab_issue_id(message: str) -> Optional[str]:
    """Parse GitLab-style issue ID."""
    return _parse_github_issue_id(message)


def _parse_generic_issue_id(message: str) -> Optional[str]:
    """Parse generic issue ID."""
    patterns = [
        r'([A-Z0-9]+-\d+)',  # Issue keys
        r'(?<!\w)\b\d+\b',  # Standalone numbers
    ]

    for pattern in patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        if matches:
            return matches[0]

    return None


# Register built-in parsers
CommitParserRegistry.register("github", _parse_github_issue_id)
CommitParserRegistry.register("gitlab", _parse_gitlab_issue_id)
CommitParserRegistry.register("generic", _parse_generic_issue_id)


def register_commit_parser(name: str, parser: Callable[[str], Optional[str]]):
    """Register a custom commit message parser."""
    CommitParserRegistry.register(name, parser)


def parse_commit_message(message: str, parser: Optional[str] = None) -> Optional[str]:
    """Parse issue ID from commit message."""
    return CommitParserRegistry.parse(message, parser)
