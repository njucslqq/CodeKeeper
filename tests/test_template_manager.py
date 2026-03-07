"""Tests for TemplateManager."""

import pytest
from pathlib import Path
from git_deep_analyzer.ai.template_manager import TemplateManager, PromptTemplate


class TestPromptTemplate:
    """Test PromptTemplate class."""

    def test_init_with_name_and_content(self):
        """Given: A name and content
        When: PromptTemplate is created
        Then: Name and content are stored correctly
        """
        # Given & When
        template = PromptTemplate(
            name="test_template",
            content="Hello {{name}}!",
            category="test"
        )

        # Then
        assert template.name == "test_template"
        assert template.content == "Hello {{name}}!"
        assert template.category == "test"

    def test_render_with_valid_context(self):
        """Given: A template with variables
        When: render() is called with valid context
        Then: Returns rendered string with variables substituted
        """
        # Given
        template = PromptTemplate(
            name="greeting",
            content="Hello {{name}}, your score is {{score}}.",
            category="test"
        )

        # When
        result = template.render(name="Alice", score=95)

        # Then
        assert result == "Hello Alice, your score is 95."

    def test_render_with_missing_variable(self):
        """Given: A template with variables
        When: render() is called without all variables
        Then: Raises KeyError or renders with empty value
        """
        # Given
        template = PromptTemplate(
            name="greeting",
            content="Hello {{name}}, your score is {{score}}.",
            category="test"
        )

        # When & Then - Jinja2 default behavior is to raise error
        with pytest.raises(KeyError):
            template.render(name="Bob")  # Missing 'score'


class TestTemplateManager:
    """Test TemplateManager class."""

    def test_init_with_templates_dir(self):
        """Given: A templates directory path
        When: TemplateManager is created
        Then: Templates directory is stored
        """
        # Given & When
        manager = TemplateManager(templates_dir=Path("/path/to/templates"))

        # Then
        assert manager.templates_dir == Path("/path/to/templates")

    def test_load_template_from_file(self, tmp_path):
        """Given: A template file in templates directory
        When: load_template() is called
        Then: Returns PromptTemplate with file content
        """
        # Given
        templates_dir = tmp_path / "templates" / "test"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "example.txt"
        template_file.write_text("Example content: {{value}}")

        manager = TemplateManager(templates_dir=templates_dir)

        # When
        template = manager.load_template("example.txt", category="test")

        # Then
        assert template.name == "example.txt"
        assert template.content == "Example content: {{value}}"
        assert template.category == "test"

    def test_load_template_caches_result(self, tmp_path):
        """Given: A template file
        When: load_template() is called twice
        Then: Second call returns cached template
        """
        # Given
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir(parents=True)
        template_file = templates_dir / "cache_test.txt"
        template_file.write_text("Cached: {{item}}")

        manager = TemplateManager(templates_dir=templates_dir)

        # When - Load twice
        template1 = manager.load_template("cache_test.txt", category="cache")
        template2 = manager.load_template("cache_test.txt", category="cache")

        # Then - Should be same object (cached)
        assert template1 is template2

    def test_load_template_file_not_found(self, tmp_path):
        """Given: TemplateManager with templates directory
        When: load_template() is called for non-existent file
        Then: Raises FileNotFoundError
        """
        # Given
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir(parents=True)
        manager = TemplateManager(templates_dir=templates_dir)

        # When & Then
        with pytest.raises(FileNotFoundError):
            manager.load_template("non_existent.txt", category="test")

    def test_load_all_templates_in_directory(self, tmp_path):
        """Given: A directory with multiple template files
        When: load_all_templates() is called
        Then: Returns all templates as dict
        """
        # Given
        templates_dir = tmp_path / "templates" / "category1"
        templates_dir.mkdir(parents=True)
        (templates_dir / "template1.txt").write_text("Content 1")
        (templates_dir / "template2.txt").write_text("Content 2")
        (templates_dir / "not_template.md").write_text("Markdown")

        manager = TemplateManager(templates_dir=templates_dir)

        # When
        templates = manager.load_all_templates()

        # Then
        assert len(templates) == 2
        assert "template1.txt" in templates
        assert "template2.txt" in templates
        assert templates["template1.txt"].name == "template1.txt"
        assert templates["template2.txt"].name == "template2.txt"

    def test_load_template_with_subcategory(self, tmp_path):
        """Given: Templates organized in subdirectories
        When: load_template() is called with subcategory path
        Then: Loads template from correct subdirectory
        """
        # Given
        templates_dir = tmp_path / "templates"
        (templates_dir / "technical").mkdir(parents=True)
        (templates_dir / "technical" / "quality.txt").write_text(
            "Analyze code quality for: {{code}}"
        )

        manager = TemplateManager(templates_dir=templates_dir)

        # When
        template = manager.load_template("technical/quality.txt", category="technical")

        # Then
        assert template.name == "quality.txt"
        assert template.content == "Analyze code quality for: {{code}}"
        assert template.category == "technical"
