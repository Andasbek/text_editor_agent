from app.service import run_text_editor_agent
from unittest.mock import patch, MagicMock

def test_run_text_editor_agent_success():
    # Mock the compiled graph
    mock_app = MagicMock()
    # History must match the grouping expectations:
    # Iter 0: Writer
    # Iter 0: Critic (Fail)
    # Iter 0 (logical end): Editor (produces edited text)
    # -- End of Block 1 --
    # Iter 1: Critic (Pass)
    
    # Wait, my logic says: Writer(Iter 0). Editor(Iter 1).
    # If Editor iteration in state is 1, then `step.get("iteration")` is 1.
    
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
        result = run_text_editor_agent("task", "generate", "")
        
        trace = result["trace"]
        # Cycle 1: Writer(D1) -> Critic(Fail) -> Editor(D2)
        # This forms ONE complete trace item.
        # Cycle 2: Critic (Pass) on D2. 
        # Since I treated Editor's output as 'edited' of item 1 AND 'draft' of item 2:
        
        # Item 1: {iter:1, draft:D1, critic:Fail, edited:D2}
        # Item 2: {iter:2, draft:D2, critic:Pass}
        
        assert len(trace) == 2
        
        assert trace[0]["draft"] == "D1"
        assert trace[0]["edited"] == "D2"
        assert trace[0]["critic"]["passed"] is False
        
        assert trace[1]["draft"] == "D2"
        assert trace[1]["critic"]["passed"] is True

def test_run_text_editor_agent_max_iterations():
    mock_app = MagicMock()
    # Provide history so it doesn't return empty/unknown
    mock_final_state = {
        "draft": "Final Text",
        "iteration": 3,
        "quality_passed": False,
        "history": [{"step": "writer", "content": "foo"}] 
    }
    mock_app.invoke.return_value = mock_final_state
    
    with patch("app.service.build_graph", return_value=mock_app):
        result = run_text_editor_agent("task", "generate", "")
        assert result["stopped_by"] == "max_iterations"
