"""Report interaction functionality."""

from typing import List, Dict, Any, Optional
from jinja2 import Template

from .models import ReportData, ReportDetailLevel


class ReportInteractions:
    """Add interactive features to reports."""

    def __init__(self):
        """Initialize report interactions."""
        self.collapse_template = self._get_collapse_template()
        self.search_template = self._get_search_template()
        self.filter_template = self._get_filter_template()
        self.detail_switcher_template = self._get_detail_switcher_template()

    def add_collapse_expand(self, report: ReportData, html: str) -> str:
        """
        Add collapse/expand functionality to HTML sections.

        Args:
            report: Report data
            html: HTML content

        Returns:
            HTML with collapse/expand functionality
        """
        # Wrap sections with collapse controls
        template = Template(self.collapse_template)
        return template.render(html=html, report=report)

    def add_search(self, html: str) -> str:
        """
        Add search functionality to HTML.

        Args:
            html: HTML content

        Returns:
            HTML with search box
        """
        template = Template(self.search_template)
        return template.render(html=html)

    def add_filter(self, html: str, filters: List[str]) -> str:
        """
        Add filter controls to HTML.

        Args:
            html: HTML content
            filters: List of filter options

        Returns:
            HTML with filter controls
        """
        template = Template(self.filter_template)
        return template.render(html=html, filters=filters)

    def add_detail_level_switcher(
        self,
        html: str,
        current_level: ReportDetailLevel
    ) -> str:
        """
        Add detail level switcher to HTML.

        Args:
            html: HTML content
            current_level: Current detail level

        Returns:
            HTML with detail level switcher
        """
        template = Template(self.detail_switcher_template)
        return template.render(html=html, current_level=current_level)

    def toggle_section(self, section_id: str) -> str:
        """
        Generate JavaScript to toggle section visibility.

        Args:
            section_id: Section element ID

        Returns:
            JavaScript code
        """
        return f"""
<script>
function toggle_{section_id}() {{
    var element = document.getElementById('{section_id}');
    if (element.style.display === 'none') {{
        element.style.display = 'block';
    }} else {{
        element.style.display = 'none';
    }}
}}
</script>
"""

    def search(self, content: str, term: str) -> str:
        """
        Search for term in content and highlight matches.

        Args:
            content: Content to search
            term: Search term

        Returns:
            Content with highlighted matches
        """
        if not term:
            return content

        # Simple highlight implementation
        highlighted = content.replace(
            term,
            f'<mark style="background-color: yellow;">{term}</mark>'
        )
        return highlighted

    def filter_by_tag(self, report: ReportData, tag: str) -> ReportData:
        """
        Filter report sections by tag.

        Args:
            report: Report data
            tag: Tag to filter by

        Returns:
            Filtered report data
        """
        filtered_sections = [
            section for section in report.sections
            if "tags" in section.metadata and tag in section.metadata["tags"]
        ]

        return ReportData(
            title=report.title,
            format=report.format,
            detail_level=report.detail_level,
            author=report.author,
            created_at=report.created_at,
            sections=filtered_sections,
            metadata=report.metadata
        )

    def add_all_interactions(
        self,
        report: ReportData,
        html: str,
        enable_collapse: bool = True,
        enable_search: bool = True,
        enable_filter: bool = True,
        enable_detail_switch: bool = True
    ) -> str:
        """
        Add all interaction features to HTML.

        Args:
            report: Report data
            html: HTML content
            enable_collapse: Enable collapse/expand
            enable_search: Enable search
            enable_filter: Enable filters
            enable_detail_switch: Enable detail level switcher

        Returns:
            Interactive HTML
        """
        interactive_html = html

        if enable_collapse:
            interactive_html = self.add_collapse_expand(report, interactive_html)

        if enable_search:
            interactive_html = self.add_search(interactive_html)

        if enable_filter:
            # Add default filters based on sections
            filters = [s.title for s in report.sections]
            interactive_html = self.add_filter(interactive_html, filters)

        if enable_detail_switch:
            interactive_html = self.add_detail_level_switcher(
                interactive_html,
                report.detail_level
            )

        return interactive_html

    def _get_collapse_template(self) -> str:
        """Get collapse/expand template."""
        return """{{ html }}

<style>
.collapse-btn {
    cursor: pointer;
    user-select: none;
}
.collapse-btn:hover {
    background-color: #e0e0e0;
}
.collapsed {
    display: none;
}
</style>

<script>
function toggleSection(elementId) {
    var section = document.getElementById(elementId);
    section.classList.toggle('collapsed');
    var btn = document.querySelector('[onclick="toggleSection(\'' + elementId + '\')"]');
    if (section.classList.contains('collapsed')) {
        btn.textContent = '+ ' + btn.textContent.substring(2);
    } else {
        btn.textContent = '- ' + btn.textContent.substring(2);
    }
}
</script>"""

    def _get_search_template(self) -> str:
        """Get search template."""
        return """
<div class="search-container" style="margin: 20px 0;">
    <input
        type="text"
        id="search-input"
        placeholder="Search report..."
        style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;"
        onkeyup="searchReport()"
    />
</div>

<script>
function searchReport() {
    var input = document.getElementById('search-input').value.toLowerCase();
    var content = document.querySelector('.content, .container');
    var sections = content.getElementsByTagName('div');

    for (var i = 0; i < sections.length; i++) {
        var text = sections[i].textContent.toLowerCase();
        if (text.includes(input)) {
            sections[i].style.display = '';
        } else {
            if (sections[i].classList.contains('section') || sections[i].classList.contains('subsection')) {
                sections[i].style.display = 'none';
            }
        }
    }
}
</script>

{{ html }}"""

    def _get_filter_template(self) -> str:
        """Get filter template."""
        return """
<div class="filter-container" style="margin: 20px 0;">
    <strong>Filter by:</strong>
    <select id="filter-select" style="margin-left: 10px; padding: 5px;" onchange="filterReport()">
        <option value="">All Sections</option>
        {% for filter in filters %}
        <option value="{{ filter }}">{{ filter }}</option>
        {% endfor %}
    </select>
</div>

<script>
function filterReport() {
    var selected = document.getElementById('filter-select').value;
    var sections = document.querySelectorAll('.section, .subsection');

    sections.forEach(function(section) {
        var title = section.querySelector('h2, h3, h4, h5, h6');
        if (title) {
            if (selected === '' || title.textContent.includes(selected)) {
                section.style.display = '';
            } else {
                section.style.display = 'none';
            }
        }
    });
}
</script>

{{ html }}"""

    def _get_detail_switcher_template(self) -> str:
        """Get detail level switcher template."""
        return """
<div class="detail-switcher" style="margin: 20px 0;">
    <strong>Detail Level:</strong>
    <button onclick="setDetailLevel('concise')" style="margin-left: 10px;">Concise</button>
    <button onclick="setDetailLevel('standard')" style="margin-left: 5px;">Standard</button>
    <button onclick="setDetailLevel('detailed')" style="margin-left: 5px;">Detailed</button>
    <span style="margin-left: 10px; color: #666;">Current: {{ current_level.value|upper }}</span>
</div>

<script>
function setDetailLevel(level) {
    // This is a placeholder - actual implementation would
    // reload the report with different detail level
    var url = new URL(window.location);
    url.searchParams.set('detail', level);
    window.location = url;
}
</script>

{{ html }}"""
