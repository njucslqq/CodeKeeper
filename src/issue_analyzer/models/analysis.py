"""Analysis related models."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalysisDimension(str, Enum):
    """Analysis dimension enumeration."""
    BUSINESS = "business"
    TECHNICAL = "technical"
    PROCESS = "process"


class AnalysisResult(BaseModel):
    """Analysis result model."""
    dimension: str = AnalysisDimension.BUSINESS
    sub_dimension: Optional[str] = None
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    risk_level: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    duration_seconds: float = 0


class AnalysisTask(BaseModel):
    """Analysis task model."""
    id: str
    issue_id: str
    status: str = TaskStatus.PENDING
    progress: float = 0.0
    dimensions: List[str] = Field(default_factory=list)
    results: List[AnalysisResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    output_format: str = "html"
