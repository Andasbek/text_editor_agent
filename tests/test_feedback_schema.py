from app.rubric import ValidationResult
import pytest

def test_rubric_schema_valid():
    """
    Test that data matching the schema is valid.
    """
    data = {
        "passed": False,
        "issues": ["Too verbose", "Unclear thesis"],
        "suggestions": ["Cut paragraph 2", "Clarify intro"],
        "style_check": "Too casual",
        "clarity_check": "Medium",
        "score": 0.5
    }
    obj = ValidationResult(**data)
    assert obj.passed is False
    assert len(obj.issues) == 2
    assert obj.score == 0.5

def test_rubric_schema_missing_fields():
    """
    Test that missing required fields raises error.
    """
    data = {
        "passed": True
        # missing others
    }
    with pytest.raises(ValueError):
        ValidationResult(**data)
