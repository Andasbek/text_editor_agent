# graph.py
from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.nodes import writer_node, critic_node, editor_node

def verify_cycle(state: AgentState) -> str:
    """
    Determines the next step after Critic.
    Ensures at least 1 cycle of editing happens, even if passed initially.
    """
    iteration = state["iteration"]
    max_iter = state.get("max_iterations", 3)
    passed = state.get("quality_passed", False)
    
    # Logic:
    # 1. If we reached max limits -> END
    if iteration >= max_iter:
        return END
    
    # 2. Key requirement: "Minimum one cycle".
    # This means if iteration is 0 (Writer -> Critic happened, but Editor hasn't run),
    # we MUST go to Editor regardless of 'passed'.
    if iteration == 0:
        return "editor"
        
    # 3. If passed is True -> END
    if passed:
        return END
        
    # 4. Otherwise -> Editor
    return "editor"


def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("editor", editor_node)
    
    # Set entry point
    workflow.set_entry_point("writer")
    
    # Edges
    workflow.add_edge("writer", "critic")
    
    # Conditional edge from Critic
    workflow.add_conditional_edges(
        "critic",
        verify_cycle,
        {
            "editor": "editor",
            END: END
        }
    )
    
    # From Editor back to Critic
    workflow.add_edge("editor", "critic")
    
    return workflow.compile()
