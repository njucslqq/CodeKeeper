"""DocLLM Parser - LLM-based document analysis."""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from .models import Document, DocumentType

if TYPE_CHECKING:
    from typing import Callable
    from .logger import AILogger


class DocLLMParser:
    """LLM驱动的文档解析器

    用于深度分析文档内容，提取需求、识别业务目标、分析设计元素
    """

    def __init__(self, ai_client: Any, logger: Optional[Any] = None):
        """初始化DocLLM Parser

        Args:
            ai_client: AI客户端
            logger: 可选的日志记录器
        """
        self.ai_client = ai_client
        self.logger = logger

    def parse_document(
        self,
        document: Document,
        dimensions: Optional[List[str]] = None
    ) -> Document:
        """使用LLM完整解析文档

        Args:
            document: 文档对象
            dimensions: 解析维度列表（requirements, goals, design）

        Returns:
            Document: 包含LLM解析结果的文档
        """
        if dimensions is None:
            dimensions = ["requirements", "goals", "design"]

        results = {}

        # 需求提取
        if "requirements" in dimensions:
            try:
                requirements_analysis = self.extract_requirements(document.content)
                results["requirements_analysis"] = requirements_analysis
                if self.logger:
                    self.logger.log_info("DocLLMParser", "Requirements extraction completed")
            except Exception as e:
                results["requirements_analysis"] = {"error": str(e)}
                if self.logger:
                    self.logger.log_error("DocLLMParser.extract_requirements", e)

        # 业务目标识别
        if "goals" in dimensions:
            try:
                goals_analysis = self.identify_goals(document.content)
                results["goals_analysis"] = goals_analysis
                if self.logger:
                    self.logger.log_info("DocLLMParser", "Goals identification completed")
            except Exception as e:
                results["goals_analysis"] = {"error": str(e)}
                if self.logger:
                    self.logger.log_error("DocLLMParser.goals", e)

        # 设计元素提取
        if "design" in dimensions:
            try:
                design_analysis = self.analyze_design_elements(document.content)
                results["design_analysis"] = design_analysis
                if self.logger:
                    self.logger.log_info("DocLLMParser", "Design elements analysis completed")
            except Exception as e:
                results["design_analysis"] = {"error": str(e)}
                if self.logger:
                    self.logger.log_error("DocLLMParser.design", e)

        # 更新文档的requirements字段
        document.requirements = results

        return document

    def parse_document_with_alignment(
        self,
        document: Document,
        code: str,
        language: str,
        dimensions: Optional[List[str]] = None
    ) -> Document:
        """解析文档并进行需求-实现对齐分析

        Args:
            document: 文档对象
            code: 实现代码
            language: 编程语言
            dimensions: 解析维度列表

        Returns:
            Document: 包含对齐分析的文档
        """
        # 先进行基础解析
        document = self.parse_document(document, dimensions)

        # 添加对齐分析
        try:
            alignment_analysis = self.analyze_alignment(
                requirements=document.content,
                code=code,
                language=language
            )
            document.requirements["alignment_analysis"] = alignment_analysis
            if self.logger:
                self.logger.log_info("DocLLMParser", "Alignment analysis completed")
        except Exception as e:
            document.requirements["alignment_analysis"] = {"error": str(e)}
            if self.logger:
                self.logger.log_error("DocLLMParser.alignment", e)

        return document

    def parse_document_with_compliance(
        self,
        document: Document,
        specification: str,
        code: str,
        language: str,
        dimensions: Optional[List[str]] = None
    ) -> Document:
        """解析文档并进行规格合规性分析

        Args:
            document: 文档对象
            specification: 规格说明
            code: 实现代码
            language: 编程语言
            dimensions: 解析维度列表

        Returns:
            Document: 包含合规性分析的文档
        """
        # 先进行基础解析
        document = self.parse_document(document, dimensions)

        # 添加合规性分析
        try:
            compliance_analysis = self.analyze_compliance(
                specification=specification,
                code=code,
                language=language
            )
            document.requirements["compliance_analysis"] = compliance_analysis
            if self.logger:
                self.logger.log_info("DocLLMParser", "Compliance analysis completed")
        except Exception as e:
            document.requirements["compliance_analysis"] = {"error": str(e)}
            if self.logger:
                self.logger.log_error("DocLLMParser.compliance", e)

        return document

    def extract_requirements(self, document: str) -> Dict[str, Any]:
        """从文档中提取需求

        Args:
            document: 文档文本

        Returns:
            需求分析结果
        """
        prompt = f"""
        Analyze the following requirements document:

        {document}

        Extract and analyze:
        1. All requirements (functional and non-functional)
        2. Priority levels for each requirement (critical/high/medium/low)
        3. Dependencies between requirements
        4. Acceptance criteria for each requirement
        5. Ambiguities or clarifications needed
        6. Requirement categories (e.g., security, usability, performance)

        Format response as JSON with keys:
        - requirements: List of requirement objects with id, description, priority, type, category
        - acceptance_criteria: List mapped to requirement IDs
        - dependencies: List of dependency relationships
        - ambiguities: List of unclear points
        - suggestions: Clarifications or improvements
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"extraction": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DocLLMParser.extract_requirements", e)
            return {"extraction": {"error": str(e)}}

    def identify_goals(self, document: str) -> Dict[str, Any]:
        """识别文档中的业务目标

        Args:
            document: 文档文本

        Returns:
            业务目标分析结果
        """
        prompt = f"""
        Analyze the following document to identify business goals and objectives:

        {document}

        Identify:
        1. Business goals and objectives
        2. Goal priorities (critical/high/medium/low)
        3. Goal categories (e.g., revenue, user experience, efficiency, security)
        4. Success metrics for each goal
        5. Relationships between goals

        Format response as JSON with keys:
        - goals: List of goals with id, name, priority, category, description
        - metrics: Suggested metrics for goal tracking
        - relationships: Goal relationships (supports/depends_on/conflicts_with)
        - gaps: Missing information needed to clarify goals
        - recommendations: Improvements to better define goals
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"identification": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DocLLMParser.identify_goals", e)
            return {"identification": {"error": str(e)}}

    def analyze_design_elements(self, document: str) -> Dict[str, Any]:
        """分析文档中的设计元素

        Args:
            document: 文档文本

        Returns:
            设计元素分析结果
        """
        prompt = f"""
        Analyze the following design document:

        {document}

        Extract:
        1. Design patterns and architecture styles
        2. Components and their responsibilities
        3. Data structures and relationships
        4. Interfaces and contracts
        5. Design trade-offs and rationale

        Format response as JSON with keys:
        - design_elements: List of design elements (patterns, components, interfaces)
        - architecture: Overall architecture description
        - components: Component breakdown with responsibilities
        - patterns: Design patterns identified
        - trade_offs: Design trade-offs and their rationale
        - suggestions: Design improvements
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"analysis": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DocLLMParser.analyze_design_elements", e)
            return {"analysis": {"error": str(e)}}

    def analyze_alignment(
        self,
        requirements: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """分析需求与实现的匹配度

        Args:
            requirements: 需求文档
            code: 实现代码
            language: 编程语言

        Returns:
            对齐分析结果
        """
        prompt = f"""
        Compare the following requirements with the {language} implementation:

        Requirements:
        {requirements}

        Implementation:
        {code}

        Analyze:
        1. Which requirements are fully implemented
        2. Which requirements are partially implemented (with gaps)
        3. Which requirements are missing
        4. Any extra features not in requirements
        5. Implementation quality for each requirement
        6. Potential issues or improvements

        Format response as JSON with keys:
        - implemented: List of fully implemented requirement IDs or descriptions
        - partial: List of partially implemented requirements with gap details
        - missing: List of unimplemented requirements
        - extra: List of features without requirements
        - coverage_score: Percentage 0-100
        - quality_score: Implementation quality score 0-100
        - issues: List of potential issues
        - recommendations: Actions to improve alignment
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"alignment": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DocLLMParser.analyze_alignment", e)
            return {"alignment": {"error": str(e)}}

    def analyze_compliance(
        self,
        specification: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """分析代码与规格说明的合规性

        Args:
            specification: 规格说明文档
            code: 实现代码
            language: 编程语言

        Returns:
            合规性分析结果
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
        5. Security requirement compliance
        6. Any specification violations

        Format response as JSON with keys:
        - compliant: Boolean overall compliance
        - violations: List of violations with severity (critical/high/medium/low)
        - compliant_items: List of items that comply
        - compliance_score: Percentage 0-100
        - security_issues: List of security concerns
        - remediation: Steps to fix violations
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"compliance": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DocLLMParser.analyze_compliance", e)
            return {"compliance": {"error": str(e)}}

    def extract_full_analysis(
        self,
        document: Document,
        code: Optional[str] = None,
        specification: Optional[str] = None,
        language: Optional[str] = None,
        features: Optional[str] = None
    ) -> Document:
        """执行完整的文档分析

        Args:
            document: 文档对象
            code: 可选的实现代码
            specification: 可选的规格说明
            language: 可选的编程语言
            features: 可选的功能列表

        Returns:
            Document: 包含完整分析的文档
        """
        if self.logger:
            self.logger.log_analysis_start("doc_llm_parser")

        # 基础解析
        document = self.parse_document(document)

        # 对齐分析（如果提供了代码）
        if code and language:
            try:
                alignment_analysis = self.analyze_alignment(
                    requirements=document.content,
                    code=code,
                    language=language
                )
                document.requirements["alignment_analysis"] = alignment_analysis
            except Exception as e:
                document.requirements["alignment_analysis"] = {"error": str(e)}
                if self.logger:
                    self.logger.log_error("DocLLMParser.full_analysis.alignment", e)

        # 合规性分析（如果提供了规格说明和代码）
        if specification and code and language:
            try:
                compliance_analysis = self.analyze_compliance(
                    specification=specification,
                    code=code,
                    language=language
                )
                document.requirements["compliance_analysis"] = compliance_analysis
            except Exception as e:
                document.requirements["compliance_analysis"] = {"error": str(e)}
                if self.logger:
                    self.logger.log_error("DocLLMParser.full_analysis.compliance", e)

        # 功能-目标映射（如果提供了功能）
        if features:
            try:
                goals_analysis = document.requirements.get("goals_analysis", {}).get("identification", {})
                goals_text = goals_analysis.get("goals", [])
                features_goals_analysis = self._analyze_features_goals_mapping(
                    goals_text, features
                )
                document.requirements["features_goals_analysis"] = features_goals_analysis
            except Exception as e:
                document.requirements["features_goals_analysis"] = {"error": str(e)}
                if self.logger:
                    self.logger.log_error("DocLLMParser.full_analysis.features_goals", e)

        if self.logger:
            self.logger.log_analysis_complete("doc_llm_parser", 0.0, success=True)

        return document

    def _analyze_features_goals_mapping(
        self,
        goals: List[Dict[str, Any]],
        features: str
    ) -> Dict[str, Any]:
        """分析功能与业务目标的映射关系

        Args:
            goals: 目标列表
            features: 功能描述

        Returns:
            功能-目标映射分析结果
        """
        prompt = f"""
        Analyze how features support business goals.

        Business Goals:
        {goals}

        Features:
        {features}

        Identify:
        1. How each feature supports specific goals
        2. Feature-goal coverage (which goals are fully/partially supported)
        3. Gaps (features needed to achieve goals)
        4. Priority recommendations

        Format response as JSON with keys:
        - feature_goal_mapping: Mapping of features to supported goals
        - coverage: Coverage analysis by goal
        - gaps: Features missing to achieve goals
        - recommendations: Prioritization suggestions
        """

        try:
            result = self.ai_client.complete_json(prompt)
            return {"mapping": result}
        except Exception as e:
            if self.logger:
                self.logger.log_error("DocLLMParser.features_goals_mapping", e)
            return {"mapping": {"error": str(e)}}
