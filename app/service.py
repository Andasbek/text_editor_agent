from app.graph import build_graph
from app.state import AgentState

def run_text_editor_agent(task: str, mode: str, user_text: str = "", max_iterations: int = 3) -> dict:
    """
    Executes the agent and returns a structured dictionary for the UI.
    """
    initial_state = {
        "task": task,
        "mode": mode,
        "user_text": user_text,
        "draft": "",
        "critique": {},
        "iteration": 0,
        "history": [],
        "max_iterations": max_iterations,
        "quality_passed": False
    }
    
    app = build_graph()
    final_state = app.invoke(initial_state)
    
    # Process history into a cleaner trace
    # We want to group by iteration if possible, or just list steps
    # For the UI requirement: trace having [ {iteration, draft, critic, edited} ]
    # The current history is just a flat list of steps. We can reformat it.
    
    trace_groups = {}
    
    for step in final_state["history"]:
        step_type = step["step"]
        # Use iteration index as key, or just sequential processing
        # Since 'iteration' in state increments at EDITOR, we need to be careful.
        # Let's simple return the raw history steps and let UI display them, 
        # OR we try to build the requested structure.
        
        # Simpler approach for now: Return the raw history, 
        # but also try to construct the 'requested' trace for the specific UI format.
        pass

    # Actually, simpler to just return the state and let UI format it, 
    # BUT the requirements asked for a specific structure. Let's build it.
    
    structured_trace = []
    current_group = {}
    
    # Iterate history to group by logical "cycle"
    # Typical flow: Writer (Draft) -> Critic -> Editor (Draft) -> Critic ...
    
    # Using a simple heuristic: Every time we see a Writer or Editor, it is a new content version.
    
    for step in final_state["history"]:
        if step["step"] in ["writer", "editor"]:
             # If we have a pending group with content, push it (though usually paired with critic)
             if current_group:
                 structured_trace.append(current_group)
                 current_group = {}
             
             current_group["draft"] = step.get("content")
             current_group["iteration"] = step.get("iteration", 0) # Writer is 0
             
        elif step["step"] == "critic":
            current_group["critic"] = step.get("feedback")
            
    if current_group:
        structured_trace.append(current_group)

    return {
        "final_text": final_state["draft"],
        "iterations": final_state["iteration"],
        "stopped_by": "passed" if final_state["quality_passed"] else "max_iterations",
        "trace": structured_trace,
        "raw_history": final_state["history"]
    }
