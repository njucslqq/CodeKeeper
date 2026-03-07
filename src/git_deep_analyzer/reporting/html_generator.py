"""HTML report generator using Jinja2."""

from pathlib import Path
from typing import Optional
from jinja2 import Template

from .models import ReportData, ReportSection


class HTMLGenerator:
    """Generate HTML reports from ReportData."""

    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize HTML generator.

        Args:
            template_path: Optional path to custom Jinja2 template
        """
        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> Template:
        """
        Load Jinja2 template.

        Returns:
            Template instance
        """
        if self.template_path and Path(self.template_path).exists():
            # Load custom template from file
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_str = f.read()
        else:
            # Use built-in template
            template_str = self._get_builtin_template()

        return Template(template_str)

    def _get_builtin_template(self) -> str:
        """Get built-in HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .meta {
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 0.9em;
        }

        h2 {
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }

        h3 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        p {
            margin-bottom: 15px;
        }

        .section {
            margin-bottom: 30px;
        }

        .subsection {
            margin-left: 20px;
            padding-left: 20px;
            border-left: 3px solid #bdc3c7;
        }

        .detail-badge {
            display: inline-block;
            padding: 4px 12px;
            background: #3498db;
            color: white;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .search-box {
            margin: 20px 0;
            padding: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            width: 100%;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }

            h1 {
                font-size: 1.8em;
            }

            .subsection {
                margin-left: 10px;
                padding-left: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ report.title }}</h1>
        <div class="meta">
            {% if report.author %}
            <strong>Author:</strong> {{ report.author }} |
            {% endif %}
            <strong>Created:</strong> {{ report.created_at[:10] }} |
            <strong>Detail Level:</strong>
            <span class="detail-badge">{{ report.detail_level.value|upper }}</span>
        </div>

        <div class="content">
            {% macro render_section(section) %}
                <div class="section">
                    {% if section.level == 1 %}
                        <h2>{{ section.title }}</h2>
                    {% elif section.level == 2 %}
                        <div class="subsection">
                            <h3>{{ section.title }}</h3>
                    {% else %}
                        <h{{ section.level }}>{{ section.title }}</h{{ section.level }}>
                    {% endif %}

                    <div class="section-content">
                        {{ section.content }}
                    </div>

                    {% if section.subsections %}
                        <div class="subsections">
                            {% for subsection in section.subsections %}
                                {{ render_section(subsection) }}
                            {% endfor %}
                        </div>
                    {% endif %}

                    {% if section.level == 2 %}
                        </div>
                    {% endif %}
                </div>
            {% endmacro %}

            {% for section in report.sections %}
                {{ render_section(section) }}
            {% endfor %}
        </div>
    </div>

    {% macro render_section(section) %}
    <div class="section">
        {% if section.level == 1 %}
            <h2>{{ section.title }}</h2>
        {% elif section.level == 2 %}
            <div class="subsection">
                <h3>{{ section.title }}</h3>
        {% else %}
            <h{{ section.level }}>{{ section.title }}</h{{ section.level }}>
        {% endif %}

        <div class="section-content">
            {{ section.content }}
        </div>

        {% if section.subsections %}
            <div class="subsections">
                {% for subsection in section.subsections %}
                    {{ render_section(subsection) }}
                {% endfor %}
            </div>
        {% endif %}

        {% if section.level == 2 %}
            </div>
        {% endif %}
    </div>
    {% endmacro %}
</body>
</html>"""

    def generate(self, report: ReportData) -> str:
        """
        Generate HTML report.

        Args:
            report: Report data

        Returns:
            HTML string
        """
        return self.template.render(report=report)

    def _render_section(self, section: ReportSection) -> str:
        """
        Render section to HTML (helper for recursive rendering).

        Args:
            section: Section to render

        Returns:
            HTML string
        """
        # This is handled by Jinja2 macro in template
        return f"<div>{section.content}</div>"

    def save_to_file(self, report: ReportData, output_path: str) -> None:
        """
        Generate and save HTML report to file.

        Args:
            report: Report data
            output_path: Path to output HTML file
        """
        html = self.generate(report)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
