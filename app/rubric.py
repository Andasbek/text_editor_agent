from typing import List, Optional
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    passed: bool = Field(..., description="Whether the text meets all criteria")
    issues: List[str] = Field(default_factory=list, description="List of specific problems found")
    suggestions: List[str] = Field(default_factory=list, description="Specific actions to fix the problems")
    style_check: str = Field(..., description="Assessment of style/audience fit")
    clarity_check: str = Field(..., description="Assessment of clarity and structure")
    score: float = Field(..., description="Quality score from 0.0 to 1.0")

class ReportStep(BaseModel):
    step_type: str  # 'writer', 'critic', 'editor'
    content: str
    feedback: Optional[ValidationResult] = None
