"""Multi-detail-level report generation."""

from typing import Dict, List, Optional
from copy import deepcopy

from .models import ReportData, ReportSection, ReportDetailLevel


class ReportDetailAdapter:
    """Adapt reports to different detail levels."""

    # Section types to include at each detail level
    CONCISE_TYPES = {"summary", "overview", "executive"}
    STANDARD_TYPES = {"summary", "overview", "executive", "technical", "analysis"}
    DETAILED_TYPES = None  # Include all types

    def __init__(self):
        """Initialize report detail adapter."""
        pass

    def adapt_to_concise(self, report: ReportData) -> ReportData:
        """
        Convert report to concise detail level.

        Args:
            report: Source report

        Returns:
            Concise report with summary only
        """
        filtered_sections = self._filter_sections_by_types(
            report.sections,
            self.CONCISE_TYPES
        )

        # Apply content truncation
        filtered_sections = [
            self._truncate_section_content(section, max_length=200)
            for section in filtered_sections
        ]

        return self._create_adapted_report(
            report,
            ReportDetailLevel.CONCISE,
            filtered_sections
        )

    def adapt_to_standard(self, report: ReportData) -> ReportData:
        """
        Convert report to standard detail level.

        Args:
            report: Source report

        Returns:
            Standard report with balanced detail
        """
        filtered_sections = self._filter_sections_by_types(
            report.sections,
            self.STANDARD_TYPES
        )

        # Moderate content truncation
        filtered_sections = [
            self._truncate_section_content(section, max_length=500)
            for section in filtered_sections
        ]

        return self._create_adapted_report(
            report,
            ReportDetailLevel.STANDARD,
            filtered_sections
        )

    def adapt_to_detailed(self, report: ReportData) -> ReportData:
        """
        Convert report to detailed detail level.

        Args:
            report: Source report

        Returns:
            Detailed report with full content
        """
        # Keep all sections, no truncation
        sections = deepcopy(report.sections)

        # Process subsections recursively
        for section in sections:
            self._process_subsections_detailed(section)

        return self._create_adapted_report(
            report,
            ReportDetailLevel.DETAILED,
            sections
        )

    def adapt_to_level(
        self,
        report: ReportData,
        level: ReportDetailLevel
    ) -> ReportData:
        """
        Adapt report to specified detail level.

        Args:
            report: Source report
            level: Target detail level

        Returns:
            Adapted report
        """
        if level == ReportDetailLevel.CONCISE:
            return self.adapt_to_concise(report)
        elif level == ReportDetailLevel.STANDARD:
            return self.adapt_to_standard(report)
        elif level == ReportDetailLevel.DETAILED:
            return self.adapt_to_detailed(report)
        else:
            # Default to standard
            return self.adapt_to_standard(report)

    def generate_all_levels(self, report: ReportData) -> Dict[ReportDetailLevel, ReportData]:
        """
        Generate reports for all detail levels.

        Args:
            report: Source report

        Returns:
            Dictionary mapping detail levels to reports
        """
        return {
            ReportDetailLevel.CONCISE: self.adapt_to_concise(report),
            ReportDetailLevel.STANDARD: self.adapt_to_standard(report),
            ReportDetailLevel.DETAILED: self.adapt_to_detailed(report)
        }

    def filter_sections_by_type(
        self,
        report: ReportData,
        section_type: str
    ) -> List[ReportSection]:
        """
        Filter report sections by type metadata.

        Args:
            report: Report data
            section_type: Type to filter by

        Returns:
            Filtered sections list
        """
        return [
            section for section in report.sections
            if section.metadata.get("type", "").lower() == section_type.lower()
        ]

    def _filter_sections_by_types(
        self,
        sections: List[ReportSection],
        allowed_types: Optional[set]
    ) -> List[ReportSection]:
        """
        Filter sections by allowed types.

        Args:
            sections: List of sections
            allowed_types: Set of allowed types (None = all types)

        Returns:
            Filtered sections
        """
        if allowed_types is None:
            return deepcopy(sections)

        filtered = []
        for section in sections:
            section_type = section.metadata.get("type", "").lower()
            if section_type in allowed_types:
                # Keep section and process subsections
                section_copy = deepcopy(section)
                section_copy.subsections = self._filter_sections_by_types(
                    section.subsections,
                    allowed_types
                )
                filtered.append(section_copy)

        return filtered

    def _truncate_section_content(
        self,
        section: ReportSection,
        max_length: int = 200
    ) -> ReportSection:
        """
        Truncate section content to max length.

        Args:
            section: Section to truncate
            max_length: Maximum length in characters

        Returns:
            Truncated section
        """
        section_copy = deepcopy(section)

        # Truncate main content
        if len(section_copy.content) > max_length:
            section_copy.content = (
                section_copy.content[:max_length].rsplit(' ', 1)[0] + "..."
            )

        # Process subsections
        section_copy.subsections = [
            self._truncate_section_content(sub, max_length=max_length // 2)
            for sub in section_copy.subsections
        ]

        return section_copy

    def _process_subsections_detailed(self, section: ReportSection) -> None:
        """
        Process subsections for detailed report (no changes needed).

        Args:
            section: Section with subsections
        """
        # Keep all subsections as-is for detailed view
        for subsection in section.subsections:
            self._process_subsections_detailed(subsection)

    def _create_adapted_report(
        self,
        original: ReportData,
        level: ReportDetailLevel,
        sections: List[ReportSection]
    ) -> ReportData:
        """
        Create adapted report from original.

        Args:
            original: Original report
            level: New detail level
            sections: Adapted sections

        Returns:
            New report data
        """
        return ReportData(
            title=original.title,
            format=original.format,
            detail_level=level,
            author=original.author,
            created_at=original.created_at,
            sections=sections,
            metadata=deepcopy(original.metadata)
        )
