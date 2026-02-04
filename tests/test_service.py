from app.service import run_text_editor_agent
from unittest.mock import patch, MagicMock

def test_run_text_editor_agent_success():
    # Mock the compiled graph
    mock_app = MagicMock()
    mock_final_state = {
        "draft": "Final Text",
        "iteration": 2,
        "quality_passed": True,
        "history": [
            {"step": "writer", "content": "D1", "iteration": 0},
            {"step": "critic", "feedback": {"passed": False}},
            {"step": "editor", "content": "D2", "iteration": 1},
            {"step": "critic", "feedback": {"passed": True}}
        ]
    }
    mock_app.invoke.return_value = mock_final_state
    
    with patch("app.service.build_graph", return_value=mock_app):
        result = run_text_editor_agent("task", "generate")
        
        assert result["final_text"] == "Final Text"
        assert result["iterations"] == 2
        assert result["stopped_by"] == "passed"
        
        # Verify trace structure
        trace = result["trace"]
        assert len(trace) == 2
        
        # Iteration 1 (Writer)
        assert trace[0]["draft"] == "D1"
        assert trace[0]["critic"]["passed"] is False
        
        # Iteration 2 (Editor)
        assert trace[1]["draft"] == "D2"
        assert trace[1]["critic"]["passed"] is True

def test_run_text_editor_agent_max_iterations():
    mock_app = MagicMock()
    mock_final_state = {
        "draft": "Final Text",
        "iteration": 3,
        "quality_passed": False,
        "history": []
    }
    mock_app.invoke.return_value = mock_final_state
    
    with patch("app.service.build_graph", return_value=mock_app):
        result = run_text_editor_agent("task", "generate")
        assert result["stopped_by"] == "max_iterations"
