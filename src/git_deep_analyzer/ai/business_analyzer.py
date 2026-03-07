"""Business dimension analyzers."""

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


class RequirementsAnalyzer(BaseAnalyzer):
    """Requirements extraction and analysis analyzer."""

    def analyze(self, document: str, **kwargs) -> Dict[str, Any]:
        """
        Extract and analyze requirements from document.

        Args:
            document: Requirements document text

        Returns:
            Requirements analysis results
        """
        prompt = f"""
        Analyze the following requirements document:

        {document}

        Extract and analyze:
        1. All requirements (functional and non-functional)
        2. Priority levels for each requirement
        3. Dependencies between requirements
        4. Acceptance criteria for each requirement
        5. Ambiguities or clarifications needed

        Format response as JSON with keys:
        - requirements (list of requirement objects with id, description, priority, type)
        - acceptance_criteria (list mapped to requirement IDs)
        - dependencies (list of dependency relationships)
        - ambiguities (list of unclear points)
        - suggestions (clarifications or improvements)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"requirements": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("RequirementsAnalyzer", e)
            return {"requirements": {"error": str(e)}}


class AlignmentAnalyzer(BaseAnalyzer):
    """Requirements-to-implementation alignment analyzer."""

    def analyze(
        self,
        requirements: str,
        code: str,
        language: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze alignment between requirements and implementation.

        Args:
            requirements: Requirements document
            code: Implementation code
            language: Programming language

        Returns:
            Alignment analysis results
        """
        prompt = f"""
        Compare the following requirements with the {language} implementation:

        Requirements:
        {requirements}

        Implementation:
        {code}

        Analyze:
        1. Which requirements are implemented
        2. Which requirements are partially implemented
        3. Which requirements are missing
        4. Any extra features not in requirements
        5. Implementation quality for each requirement

        Format response as JSON with keys:
        - implemented (list of fully implemented requirement IDs)
        - partial (list of partially implemented with gap details)
        - missing (list of unimplemented requirements)
        - extra (list of features without requirements)
        - coverage_score (percentage 0-100)
        - recommendations (actions to improve alignment)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"alignment": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("AlignmentAnalyzer", e)
            return {"alignment": {"error": str(e)}}


class ComplianceAnalyzer(BaseAnalyzer):
    """Specification compliance analyzer."""

    def analyze(
        self,
        specification: str,
        code: str,
        language: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze code compliance with specification.

        Args:
            specification: Specification document
            code: Implementation code
            language: Programming language

        Returns:
            Compliance analysis results
        """
        prompt = f"""
        Check if the following {language} code complies with the specification:

        Specification:
        {specification}

        Code:
        {code}

        Verify:
        1. API contract compliance
        2. Data format compliance
        3. Error handling compliance
        4. Performance requirement compliance
        5. Any specification violations

        Format response as JSON with keys:
        - compliant (boolean overall compliance)
        - violations (list of violations with severity)
        - compliant_items (list of items that comply)
        - compliance_score (percentage 0-100)
        - remediation (steps to fix violations)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"compliance": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("ComplianceAnalyzer", e)
            return {"compliance": {"error": str(e)}}


class GoalsAnalyzer(BaseAnalyzer):
    """Business goals and objectives analyzer."""

    def analyze(
        self,
        document: Optional[str] = None,
        goals: Optional[str] = None,
        features: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze business goals and feature alignment.

        Args:
            document: Business goals document (alternative to goals parameter)
            goals: Goals text
            features: Feature list/description

        Returns:
            Goals analysis results
        """
        if document:
            goals_text = document
        elif goals:
            goals_text = goals
        else:
            goals_text = ""

        features_text = features or ""

        prompt = f"""
        Analyze business goals and feature alignment.

        Business Goals:
        {goals_text}

        Features:
        {features_text}

        Identify:
        1. Business goals and objectives
        2. How features support each goal
        3. Goal achievement metrics
        4. Missing features needed for goals

        Format response as JSON with keys:
        - goals (list of goals with priorities)
        - goal_feature_mapping (mapping of goals to supporting features)
        - metrics (suggested metrics for goal tracking)
        - gaps (features missing to achieve goals)
        - recommendations (improvements to better align)
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"goals": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("GoalsAnalyzer", e)
            return {"goals": {"error": str(e)}}


class BusinessAnalyzer:
    """Main business analyzer that orchestrates all sub-analyzers."""

    def __init__(self, ai_client, config: Dict[str, Any] = None, logger=None):
        """
        Initialize business analyzer.

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
            "requirements": RequirementsAnalyzer(ai_client, logger),
            "alignment": AlignmentAnalyzer(ai_client, logger),
            "compliance": ComplianceAnalyzer(ai_client, logger),
            "goals": GoalsAnalyzer(ai_client, logger),
        }

        # Filter analyzers based on config
        enabled_analyzers = self.config.get("analyzers", list(self.analyzers.keys()))
        self.analyzers = {
            k: v for k, v in self.analyzers.items()
            if k in enabled_analyzers
        }

    def analyze(
        self,
        document: str,
        dimensions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze business document for specified dimensions.

        Args:
            document: Document text
            dimensions: List of dimensions to analyze (default: all)
            **kwargs: Additional parameters for specific analyzers

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
                    # Pass document to requirements and goals analyzers
                    if dimension in ["requirements", "goals"]:
                        result = analyzer.analyze(document=document, **kwargs)
                    else:
                        result = analyzer.analyze(**kwargs)
                    results.update(result)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error(f"BusinessAnalyzer.{dimension}", e)
                    results[dimension] = {"error": str(e)}

        return results

    def analyze_all(
        self,
        requirements: str,
        code: str,
        language: str,
        specification: Optional[str] = None,
        document: Optional[str] = None,
        features: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze all business dimensions.

        Args:
            requirements: Requirements document
            code: Implementation code
            language: Programming language
            specification: Optional specification document
            document: Optional business goals document
            features: Optional feature list
            **kwargs: Additional parameters

        Returns:
            Combined analysis results
        """
        if self.logger:
            self.logger.log_analysis_start("business")

        results = {}

        # Requirements analyzer
        if "requirements" in self.analyzers:
            try:
                result = self.analyzers["requirements"].analyze(document=requirements or document)
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("BusinessAnalyzer.requirements", e)
                results["requirements"] = {"error": str(e)}

        # Alignment analyzer
        if "alignment" in self.analyzers:
            try:
                result = self.analyzers["alignment"].analyze(
                    requirements=requirements,
                    code=code,
                    language=language
                )
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("BusinessAnalyzer.alignment", e)
                results["alignment"] = {"error": str(e)}

        # Compliance analyzer
        if "compliance" in self.analyzers and specification:
            try:
                result = self.analyzers["compliance"].analyze(
                    specification=specification,
                    code=code,
                    language=language
                )
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("BusinessAnalyzer.compliance", e)
                results["compliance"] = {"error": str(e)}

        # Goals analyzer
        if "goals" in self.analyzers:
            try:
                result = self.analyzers["goals"].analyze(
                    document=document,
                    features=features
                )
                results.update(result)
            except Exception as e:
                if self.logger:
                    self.logger.log_error("BusinessAnalyzer.goals", e)
                results["goals"] = {"error": str(e)}

        if self.logger:
            self.logger.log_analysis_complete("business", 0.0, success=True)

        return results
