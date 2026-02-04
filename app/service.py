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
    
    # Process history into structured trace
    # Goal: [ {iteration: 0, draft: "...", critic: {...}, edited: "..."} ]
    
    structured_trace = []
    
    # We will build a map: iteration_id -> dict
    iterations_map = {}
    
    for step in final_state["history"]:
        step_type = step["step"]
        # Logic: Writer starts iter 0. Editor starts iter 1, 2...
        # Critic belongs to the previous content generation.
        
        # However, the node logic in nodes.py says:
        # Writer -> iter 0
        # Editor -> increments iter -> returns new iter
        
        # So:
        # writer output: iter 0
        # critic output: no iter change, belongs to current draft
        # editor output: iter N+1
        
        # Let's rely on the order of appearance.
        # Sequence: writer(0) -> critic -> editor(1) -> critic ...
        
        # We need to robustly assign steps to an iteration bucket.
        # Writer sets the baseline for iter 0.
        
        if step_type == "writer":
            i = 0
            if i not in iterations_map: iterations_map[i] = {"iteration": i}
            iterations_map[i]["draft"] = step.get("content")
            
        elif step_type == "editor":
            i = step.get("iteration")
            # Editor output IS the "draft" of the NEW iteration 
            # OR we can treat it as "edited" version of previous?
            # The Requirement says: {draft, critic, edited}
            # This implies one object per cycle.
            # Cycle 1: drafted (writer) -> critiqued -> edited (editor).
            # Cycle 2: drafted (which is the output of editor from prev?) -> ...
            
            # Let's treat Editor output as "edited" field of the CURRENT cycle.
            # Then that "edited" text becomes the "draft" for the next cycle implicitly?
            # Or we just start a New Cycle object?
            
            # The requirement example:
            # {iteration: 1, draft: "...", critic: {...}, edited: "..."}
            
            # This perfectly maps to: Writer(draft) -> Critic -> Editor(edited).
            # But what about next loop? Graph goes Editor -> Critic directly. 
            # So Editor output IS the draft for the next critic.
            
            # Revised Logic based on Graph Flow:
            # Flow: Writer -> Critic -> Editor -> Critic -> Editor ...
            
            # Group 0: Writer(draft), Critic
            # Group 1: Editor(draft/edited?), Critic
            
            # If we want "draft -> critic -> edited" structure, it implies:
            # 1. Start with some text (Writer)
            # 2. Get critique
            # 3. Produce fix (Editor)
            # This fits perfectly.
            
            # But subsequent loops in LangGraph are Editor -> Critic.
            # So Editor is producing the text that is then critiqued.
            # So Editor's output serves as "Draft" for the NEXT critique, 
            # AND "Edited" result of the PREVIOUS critique.
            
            # Let's map strictly by "iteration" stored in state?
            # Writer: returns iter 0.
            # Editor: returns iter N.
            
            # So:
            # Writer(iter 0) -> bucket 0 'draft'
            # Critic (follows writer) -> bucket 0 'critic'
            # Editor (follows critic, returns iter 1) -> bucket 0 'edited'? OR bucket 1 'draft'?
            
            # If we put Editor output into Bucket 0 as 'edited', 
            # then Bucket 1 starts with... ? The next Critic?
            
            # Let's try to group pairs of Content + Critique.
            # Step Sequence in history:
            # 1. Writer (content)
            # 2. Critic (feedback)
            # 3. Editor (content)
            # 4. Critic (feedback)
            
            # We can group these linearly.
            # Node 'writer' or 'editor' -> New Trace Entry with 'draft'
            # Node 'critic' -> Enrich last Trace Entry with 'critic'
            
            # Wait, the prompt requirements said: {draft, critic, edited}
            # This implies a triple.
            # But the graph is Writer->Critic (check)->Editor.
            # Only if check fails we get Editor.
            
            # If check fails: Writer -> Critic -> Editor. That's a triple.
            # If check passes: Writer -> Critic. That's a pair.
            
            # Let's support both.
            # We will maintain a "current_cycle" dict.
            # When we see Writer or Editor:
            # - If we have a 'draft' already in current_cycle, and we see Editor:
            #   It means we are doing the 'edited' part.
            # - Wait, Editor produces content.
            
            pass 
        
    # Implementation of Linear Scan Grouping
    trace_list = []
    current_block = {}
    
    for step in final_state["history"]:
        step_type = step["step"]
        
        if step_type == "writer":
            # Always starts a new block
            if current_block: trace_list.append(current_block)
            current_block = {
                "iteration": step.get("iteration", 0) + 1, # 1-based index for UI convenience? Or use state?
                # Let's use 1-based index for UI consistency
                "draft": step.get("content")
            }
            
        elif step_type == "critic":
            current_block["critic"] = step.get("feedback")
            
        elif step_type == "editor":
            # This is the "correction" of the current block
            current_block["edited"] = step.get("content")
            # The editor output effectively becomes the 'draft' for the next potential critic loop
            # BUT we want to visualize it as the 'result' of this iteration.
            
            # If the loop continues, the NEXT critic will operate on this 'edited' text.
            # So we should close this block and start a new one?
            # If we close it, the next block has no 'draft' (unless we duplicate).
            
            # Let's try: One block per Critic evaluation?
            # No, user wants "Draft -> Critic -> Edited".
            
            # So:
            # Block 1: Writer(Draft) -> Critic -> Editor(Edited)
            # Block 2: (Edited text from B1 is input) -> Critic -> Editor(Edited)
            
            # So if we hit Editor, we attach it to 'edited', finish the block, 
            # AND potentially start a new block with 'draft' = that same text,
            # IN CASE there is another Critic step coming.
            
            # Look ahead? Or just post-process?
            pass

    # Efficient post-processing loop
    refined_trace = []
    
    # Flatten checks
    history = final_state["history"]
    # Flatten checks
    history = final_state["history"]
    if not history:
        return {
            "final_text": "",
            "iterations": 0,
            "stopped_by": "unknown",
            "trace": [],
            "raw_history": []
        }
    
    # We'll treat every "Content" generating step (Writer/Editor) as a potential 'draft' 
    # for a critique.
    # An 'Editor' step is ALSO the 'edited' result of the previous 'draft'.
    
    # Step 0: Writer -> Draft[0]
    # Step 1: Critic -> Critic[0]
    # Step 2: Editor -> Edited[0] AND Draft[1]
    # Step 3: Critic -> Critic[1]
    # Step 4: Editor -> Edited[1] AND Draft[2]
    
    # Let's build exactly this structure.
    
    # We need a list of content steps.
    content_steps = [s for s in history if s["step"] in ["writer", "editor"]]
    critic_steps = [s for s in history if s["step"] == "critic"]
    
    # We assume strict alternation enforced by graph, but let's be safe.
    # The safest is strict sequential scan.
    
    current_item = {}
    
    for step in history:
        s_type = step["step"]
        
        if s_type == "writer":
            # Start of everything
            current_item = {"iteration": 1, "draft": step["content"]}
            
        elif s_type == "critic":
            current_item["critic"] = step["feedback"]
            
        elif s_type == "editor":
            # Validation: belongs to current_item
            current_item["edited"] = step["content"]
            refined_trace.append(current_item)
            
            # PREPARE next item, using this edited text as the new draft
            # iteration count increments
            next_iter = current_item["iteration"] + 1
            current_item = {"iteration": next_iter, "draft": step["content"]}

    # If the last item has a draft (and maybe critique) but no editor (process ended/passed),
    # we still append it so user sees the final state check.
    if "draft" in current_item and current_item not in refined_trace:
        refined_trace.append(current_item)

    return {
        "final_text": final_state["draft"],
        "iterations": final_state["iteration"],
        "stopped_by": "passed" if final_state["quality_passed"] else "max_iterations",
        "trace": refined_trace,
        "raw_history": final_state["history"]
    }
