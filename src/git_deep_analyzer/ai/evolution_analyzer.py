"""Evolution dimension analyzers."""

from typing import Dict, Any, List, Optional


class BaseAnalyzer:
    """Base class for all analyzers."""

    def __init__(self, ai_client, logger=None):
        """
        Initialize analyzer.

        Args:
            ai_client: AI client for analysis
            logger: Optional logger instance
        """
        self.ai_client = ai_client
        self.logger = logger

    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        Analyze input.

        Args:
            **kwargs: Analysis-specific parameters

        Returns:
            Analysis results dictionary
        """
        raise NotImplementedError


class TimelineAnalyzer(BaseAnalyzer):
    """Timeline and evolution pattern analyzer."""

    def analyze(self, commits: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze commit timeline and evolution patterns.

        Args:
            commits: Commit history or summary

        Returns:
            Timeline analysis results
        """
        prompt = f"""
        Analyze the following commit history for evolution patterns:

        {commits}

        Identify:
        1. Development phases and periods
        2. Activity patterns (when commits occur)
        3. Velocity changes over time
        4. Major milestones or releases
        5. Evolution trends (stability vs. rapid change)

        Format response as JSON with keys:
        - phases (list of development phases with time ranges)
        - patterns (activity patterns observed)
        - velocity (commit rate trends)
        - milestones (major events/releases)
        - trends (overall evolution direction)
        - insights (key observations)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"timeline": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("TimelineAnalyzer", e)
            return {"timeline": {"error": str(e)}}


class ImpactAnalyzer(BaseAnalyzer):
    """Impact analysis for code changes."""

    def analyze(
        self,
        diff: str,
        code: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze impact of code changes.

        Args:
            diff: Diff or change description
            code: Current code (optional)
            language: Programming language (optional)

        Returns:
            Impact analysis results
        """
        code_text = code or ""
        lang_text = language or "unknown"

        current_code_part = ""
        if code_text:
            current_code_part = f"\nCurrent Code ({lang_text}):\n{code_text}\n"

        prompt = f"""
        Analyze the impact of the following code changes:

        Changes/Diff:
        {diff}
        {current_code_part}

        Assess:
        1. Affected components and areas
        2. Risk level (low/medium/high)
        3. Potential breaking changes
        4. Dependencies impacted
        5. Performance implications

        Format response as JSON with keys:
        - affected_areas (list of components impacted)
        - risk_level (low/medium/high with reasoning)
        - breaking_changes (list of potential breaking changes)
        - dependencies (affected dependencies)
        - performance_impact (potential performance effects)
        - recommendations (mitigation strategies)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"impact": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("ImpactAnalyzer", e)
            return {"impact": {"error": str(e)}}


class DebtAnalyzer(BaseAnalyzer):
    """Technical debt analyzer."""

    def analyze(
        self,
        code: str,
        language: str,
        commits: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze technical debt.

        Args:
            code: Source code
            language: Programming language
            commits: Optional commit history context

        Returns:
        Technical debt analysis results
        """
        commits_text = commits or ""
        commits_part = ""
        if commits_text:
            commits_part = f"Commit Context:\n{commits_text}\n"

        prompt = f"""
        Analyze the following {language} code for technical debt:

        Code:
        {code}

        {commits_part}

        Identify:
        1. Code smells and anti-patterns
        2. Complexity issues
        3. Duplicate code
        4. Outdated patterns or dependencies
        5. Missing tests or documentation
        6. Performance issues

        Categorize debt by type:
        - Complexity debt
        - Duplication debt
        - Documentation debt
        - Test debt
        - Design debt
        - Infrastructure debt

        Format response as JSON with keys:
        - debt_items (list of debt items with type, severity, location)
        - debt_by_type (summary by debt category)
        - severity_summary (count by severity level)
        - remediation (prioritized list of fixes)
        - effort_estimate (effort to resolve each debt item)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"debt": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DebtAnalyzer", e)
            return {"debt": {"error": str(e)}}


class EvolutionAnalyzer:
    """Main evolution analyzer that orchestrates all sub-analyzers."""

    def __init__(self, ai_client, config: Dict[str, Any] = None, logger=None):
        """
        Initialize evolution analyzer.

        Args:
            ai_client: AI client for analysis
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.ai_client = ai_client
        self.config = config or {}
        self.logger = logger

        # Initialize analyzers
        self.analyzers = {
            "timeline": TimelineAnalyzer(ai_client, logger),
            "impact": ImpactAnalyzer(ai_client, logger),
            "debt": DebtAnalyzer(ai_client, logger),
        }

        # Filter analyzers based on config
        enabled_analyzers = self.config.get("analyzers", list(self.analyzers.keys()))
        self.analyzers = {
            k: v for k, v in self.analyzers.items()
            if k in enabled_analyzers
        }

    def analyze(
        self,
        commits: Optional[str] = None,
        diff: Optional[str] = None,
        code: Optional[str] = None,
        language: Optional[str] = None,
        dimensions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze evolution for specified dimensions.

        Args:
            commits: Commit history
            diff: Code diff/changes
            code: Source code
            language: Programming language
            dimensions: List of dimensions to analyze (default: all)
            **kwargs: Additional parameters

        Returns:
            Combined analysis results
        """
        if dimensions is None:
            dimensions = list(self.analyzers.keys())

        results = {}
        for dimension in dimensions:
            if dimension in self.analyzers:
                analyzer = self.analyzers[dimension]
                try:
                    # Call appropriate analyzer with parameters
                    if dimension == "timeline":
                        result = analyzer.analyze(commits=commits or "", **kwargs)
                    elif dimension == "impact":
                        result = analyzer.analyze(
                            diff=diff or "",
                            code=code,
                            language=language,
                            **kwargs
                        )
                    elif dimension == "debt":
                        result = analyzer.analyze(
                            code=code or "",
                            language=language or "unknown",
                            commits=commits,
                            **kwargs
                        )
                    else:
                        result = analyzer.analyze(**kwargs)
                    results.update(result)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error(f"EvolutionAnalyzer.{dimension}", e)
                    results[dimension] = {"error": str(e)}

        return results

    def analyze_all(
        self,
        commits: str,
        diff: str,
        code: str,
        language: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze all evolution dimensions.

        Args:
            commits: Commit history
            diff: Code diff/changes
            code: Source code
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Combined analysis results from all analyzers
        """
        if self.logger:
            self.logger.log_analysis_start("evolution")

        results = {}

        # Timeline analyzer
        if "timeline" in self.analyzers:
            try:
                result = self.analyzers["timeline"].analyze(commits=commits)
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("EvolutionAnalyzer.timeline", e)
                results["timeline"] = {"error": str(e)}

        # Impact analyzer
        if "impact" in self.analyzers:
            try:
                result = self.analyzers["impact"].analyze(
                    diff=diff,
                    code=code,
                    language=language
                )
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("EvolutionAnalyzer.impact", e)
                results["impact"] = {"error": str(e)}

        # Debt analyzer
        if "debt" in self.analyzers:
            try:
                result = self.analyzers["debt"].analyze(
                    code=code,
                    language=language,
                    commits=commits
                )
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("EvolutionAnalyzer.debt", e)
                results["debt"] = {"error": str(e)}

        if self.logger:
            self.logger.log_analysis_complete("evolution", 0.0, success=True)

        return results
