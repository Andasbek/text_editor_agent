from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from app.state import AgentState
from app.prompts import (
    WRITER_SYSTEM_PROMPT, WRITER_REVISE_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    EDITOR_SYSTEM_PROMPT
)
from app.llm import get_llm
from app.rubric import ValidationResult

def writer_node(state: AgentState) -> dict:
    """
    Generates the initial draft OR revises user input for the first time.
    """
    llm = get_llm(json_mode=False)
    
    task = state["task"]
    mode = state.get("mode", "generate")
    user_text = state.get("user_text", "")
    
    if mode == "revise" and user_text:
        # Initial revision
        prompt = WRITER_REVISE_PROMPT.format(user_text=user_text, task=task)
        messages = [HumanMessage(content=prompt)]
    else:
        # Generation from scratch
        messages = [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"Task: {task}")
        ]
        
    response = llm.invoke(messages)
    draft = response.content.strip()
    
    # Update history
    history = state.get("history", [])
    history.append({"step": "writer", "content": draft})
    
    return {
        "draft": draft,
        "iteration": 0,
        "history": history
    }

def critic_node(state: AgentState) -> dict:
    """
    Reviews the current draft.
    """
    llm = get_llm(json_mode=True)
    parser = JsonOutputParser(pydantic_object=ValidationResult)
    
    draft = state["draft"]
    task = state["task"]
    
    # Prepare prompt
    content = f"Task: {task}\n\nCurrent Draft:\n{draft}\n\nEvaluate strictly."
    messages = [
        SystemMessage(content=CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=content)
    ]
    
    response = llm.invoke(messages)
    
    try:
        critique_data = parser.parse(response.content)
    except Exception:
        # Fallback if specific parsing fails, though json_mode helps
        import json
        critique_data = json.loads(response.content)

    # Update history
    history = state.get("history", [])
    history.append({
        "step": "critic", 
        "feedback": critique_data
    })

    return {
        "critique": critique_data,
        "quality_passed": critique_data.get("passed", False),
        "history": history
    }

def editor_node(state: AgentState) -> dict:
    """
    Applies critique to the draft.
    """
    llm = get_llm(json_mode=False)
    
    draft = state["draft"]
    critique = state["critique"]
    task = state["task"]
    
    # Construct suggestions string
    suggestions = "\n- ".join(critique.get("suggestions", []))
    issues = "\n- ".join(critique.get("issues", []))
    
    prompt = f"""Original Task: {task}

Current Draft:
{draft}

Critique (Issues):
- {issues}

Suggestions for Improvement:
- {suggestions}

Please rewrite the draft incorporating these changes."""

    messages = [
        SystemMessage(content=EDITOR_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    new_draft = response.content.strip()
    
    # Increment iteration
    new_iter = state["iteration"] + 1
    
    # Update history
    history = state.get("history", [])
    history.append({
        "step": "editor",
        "content": new_draft,
        "iteration": new_iter
    })
    
    return {
        "draft": new_draft,
        "iteration": new_iter,
        "history": history
    }
