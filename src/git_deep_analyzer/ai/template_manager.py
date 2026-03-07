"""AI prompt template manager using Jinja2."""

from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, Template
import hashlib


class PromptTemplate:
    """Represents a single prompt template."""

    def __init__(self, name: str, content: str, category: str = "general"):
        """
        Initialize a prompt template.

        Args:
            name: Template name (typically filename)
            content: Template content with Jinja2 variables
            category: Template category for organization
        """
        self.name = name
        self.content = content
        self.category = category
        self._template = Environment(undefined=StrictUndefined).from_string(content)

    def render(self, **kwargs) -> str:
        """
        Render the template with given context.

        Args:
            **kwargs: Template variables

        Returns:
            Rendered string
        """
        return self._template.render(**kwargs)

    def __repr__(self) -> str:
        return f"PromptTemplate(name={self.name!r}, category={self.category!r})"


class TemplateManager:
    """Manages AI prompt templates with caching."""

    def __init__(self, templates_dir: Path):
        """
        Initialize template manager.

        Args:
            templates_dir: Root directory containing templates
        """
        self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, PromptTemplate] = {}

    def load_template(
        self,
        template_path: str,
        category: str = "general"
    ) -> PromptTemplate:
        """
        Load a single template from file.

        Args:
            template_path: Relative path from templates_dir
            category: Template category

        Returns:
            PromptTemplate instance

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Check cache
        cache_key = self._make_cache_key(template_path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load from file
        template_file = self.templates_dir / template_path
        if not template_file.exists():
            raise FileNotFoundError(
                f"Template not found: {template_file}"
            )

        content = template_file.read_text(encoding="utf-8")
        name = template_file.name

        # Create and cache template
        template = PromptTemplate(name=name, content=content, category=category)
        self._cache[cache_key] = template

        return template

    def load_all_templates(self, pattern: str = "*.txt") -> Dict[str, PromptTemplate]:
        """
        Load all templates matching pattern from templates directory.

        Args:
            pattern: Glob pattern to match files (default: *.txt)

        Returns:
            Dict mapping template names to PromptTemplate instances
        """
        templates = {}

        for template_file in self.templates_dir.glob(pattern):
            if template_file.is_file():
                try:
                    relative_path = template_file.relative_to(self.templates_dir)
                    name = str(relative_path)
                    category = relative_path.parent.name if relative_path.parent != Path(".") else "general"

                    template = self.load_template(name, category=category)
                    templates[name] = template
                except Exception as e:
                    # Log warning but continue loading other templates
                    import warnings
                    warnings.warn(f"Failed to load template {template_file}: {e}")

        return templates

    def _make_cache_key(self, template_path: str) -> str:
        """Generate cache key for template path."""
        return hashlib.md5(template_path.encode()).hexdigest()

    def clear_cache(self) -> None:
        """Clear template cache."""
        self._cache.clear()

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get cached template by name.

        Args:
            name: Template name (full path from templates_dir)

        Returns:
            PromptTemplate if cached, None otherwise
        """
        cache_key = self._make_cache_key(name)
        return self._cache.get(cache_key)
