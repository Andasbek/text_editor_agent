from app.nodes import writer_node, critic_node, editor_node
from langchain_core.messages import AIMessage
import json

def test_writer_node_generates_draft(mock_get_llm, mock_llm):
    # Setup
    mock_llm.invoke.return_value = AIMessage(content="Generated Draft Content")
    state = {"task": "Write a poem", "mode": "generate", "history": []}
    
    # Execution
    result = writer_node(state)
    
    # Verification
    assert result["draft"] == "Generated Draft Content"
    assert result["iteration"] == 0
    assert len(result["history"]) == 1
    assert result["history"][0]["step"] == "writer"
    assert result["history"][0]["content"] == "Generated Draft Content"

def test_writer_node_revises_text(mock_get_llm, mock_llm):
    mock_llm.invoke.return_value = AIMessage(content="Revised Text")
    state = {"task": "fix grammar", "mode": "revise", "user_text": "bad txt", "history": []}
    
    result = writer_node(state)
    
    assert result["draft"] == "Revised Text"
    # Check that prompt contained user_text (implementation detail check)
    args, _ = mock_llm.invoke.call_args
    prompt_str = args[0][0].content
    assert "bad txt" in prompt_str

def test_critic_node_passes(mock_get_llm, mock_llm):
    feedback = {
        "passed": True,
        "issues": [],
        "suggestions": [],
        "style_check": "Good",
        "clarity_check": "Clear",
        "score": 1.0
    }
    mock_llm.invoke.return_value = AIMessage(content=json.dumps(feedback))
    state = {"task": "t", "draft": "Perfect draft", "history": []}
    
    result = critic_node(state)
    
    assert result["quality_passed"] is True
    assert result["critique"]["score"] == 1.0
    assert len(result["history"]) == 1
    assert result["history"][0]["step"] == "critic"

def test_critic_node_fails(mock_get_llm, mock_llm):
    feedback = {
        "passed": False,
        "issues": ["typo"],
        "suggestions": ["fix it"],
        "style_check": "Bad",
        "clarity_check": "Bad",
        "score": 0.5
    }
    mock_llm.invoke.return_value = AIMessage(content=json.dumps(feedback))
    state = {"task": "t", "draft": "Bad draft", "history": []}
    
    result = critic_node(state)
    
    assert result["quality_passed"] is False

def test_editor_node(mock_get_llm, mock_llm):
    mock_llm.invoke.return_value = AIMessage(content="Edited Draft")
    state = {
        "task": "t",
        "draft": "Old Draft",
        "critique": {"issues": ["error"], "suggestions": ["fix"]},
        "iteration": 0,
        "history": []
    }
    
    result = editor_node(state)
    
    assert result["draft"] == "Edited Draft"
    assert result["iteration"] == 1
    assert len(result["history"]) == 1
    assert result["history"][0]["step"] == "editor"
