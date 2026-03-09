"""P1.5 Commit message parser tests."""

import re


def test_parse_issue_id_github():
    from issue_analyzer.parsers import parse_commit_message
    message = "Fix #PROJ-123: some description"
    result = parse_commit_message(message, "github")
    assert result == "PROJ-123"


def test_parse_issue_id_multiple():
    from issue_analyzer.parsers import parse_commit_message
    message = "PROJ-123, PROJ-456: fix multiple issues"
    result = parse_commit_message(message, "generic")
    assert "PROJ-123" in result


def test_parser_registry():
    from issue_analyzer.parsers import CommitParserRegistry
    from issue_analyzer.parsers import register_commit_parser

    # Register a custom parser
    def custom_parser(message: str) -> str:
        return "CUSTOM-123"

    register_commit_parser("custom", custom_parser)

    # Verify it's registered
    assert "custom" in CommitParserRegistry._parsers


def test_parse_with_registered_parser():
    from issue_analyzer.parsers import parse_commit_message, register_commit_parser

    # Register a parser
    def custom_parser(message: str) -> str:
        if "CUSTOM" in message:
            return "FOUND-CUSTOM"
        return None

    register_commit_parser("custom", custom_parser)

    # Parse with custom parser
    result = parse_commit_message("This is a CUSTOM issue", parser="custom")
    assert result == "FOUND-CUSTOM"
