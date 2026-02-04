from app.graph import build_graph
from langchain_core.messages import AIMessage
import json
import pytest

def test_full_flow_success(mock_get_llm, mock_llm):
    """
    Simulates: Writer -> Critic (Fail) -> Editor -> Critic (Pass)
    """
    # Define sequence of responses
    writer_resp = AIMessage(content="Draft 1")
    critic_fail = AIMessage(content=json.dumps({
        "passed": False, "issues": ["bad"], "suggestions": ["fix"], 
        "style_check": "ok", "clarity_check": "ok", "score": 0.5
    }))
    editor_resp = AIMessage(content="Draft 2")
    critic_pass = AIMessage(content=json.dumps({
        "passed": True, "issues": [], "suggestions": [], 
        "style_check": "ok", "clarity_check": "ok", "score": 1.0
    }))
    
    mock_llm.invoke.side_effect = [
        writer_resp, 
        critic_fail, 
        editor_resp, 
        critic_pass
    ]
    
    app = build_graph()
    initial_state = {
        "task": "Test Task", 
        "mode": "generate", 
        "iteration": 0,
        "history": [],
        "max_iterations": 3
    }
    
    final = app.invoke(initial_state)
    
    assert final["draft"] == "Draft 2"
    assert final["quality_passed"] is True
    # Iteration: Writer(0) -> Critic(Fail) -> Editor(1) -> Critic(Pass)
    assert final["iteration"] == 1 
    assert len(final["history"]) == 4 # Writer, Critic, Editor, Critic

def test_max_iterations_limit(mock_get_llm, mock_llm):
    """
    Simulates explicit failure loop until max iterations
    """
    writer_resp = AIMessage(content="Draft")
    critic_fail = AIMessage(content=json.dumps({
        "passed": False, "issues": ["bad"], "suggestions": ["fix"], 
        "style_check": "ok", "clarity_check": "ok", "score": 0.5
    }))
    editor_resp = AIMessage(content="Draft Edited")
    
    # Infinite sequence of Fail -> Edit -> Fail ...
    mock_llm.invoke.side_effect = [writer_resp] + [critic_fail, editor_resp] * 10
    
    app = build_graph()
    initial_state = {
        "task": "Test Task", 
        "mode": "generate", 
        "iteration": 0, 
        "history": [],
        "max_iterations": 2
    }
    
    final = app.invoke(initial_state)
    
    # Should stop at iteration 2
    assert final["iteration"] == 2
    assert final["quality_passed"] is False
