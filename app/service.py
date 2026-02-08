# service.py
from __future__ import annotations

from typing import Any, Dict, List

from app.graph import build_graph


def run_text_editor_agent(task: str, mode: str, user_text: str, max_iterations: int = 3) -> Dict[str, Any]:
    """
    Service layer: runs the LangGraph agent and returns a UI/CLI-friendly result.

    Returns:
      {
        "final_text": str,
        "iterations": int,
        "stopped_by": "passed" | "max_iterations",
        "trace": [
            {"iteration": int, "draft": str, "critic": dict|None, "edited": str|None},
            ...
        ],
        "raw_history": list
      }
    """
    initial_state: Dict[str, Any] = {
        "task": task,
        "mode": mode,
        "user_text": user_text or "",
        "draft": "",
        "critique": {},
        "iteration": 0,
        "history": [],
        "max_iterations": max_iterations,
        "quality_passed": False,
    }

    app = build_graph()
    final_state: Dict[str, Any] = app.invoke(initial_state)

    raw_history: List[dict] = final_state.get("history", [])

    # Build a clean trace for UI:
    # Iteration 0: draft from writer -> critic -> edited (from editor)
    # Iteration 1..N: draft (previous edited) -> critic -> edited ...
    trace: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None

    last_draft: str = ""
    current_iteration: int = 0

    for step in raw_history:
        step_type = step.get("step")

        if step_type == "writer":
            # Start iteration 0 with draft from writer
            current_iteration = 0
            last_draft = step.get("content", "")
            current = {
                "iteration": current_iteration,
                "draft": last_draft,
                "critic": None,
                "edited": None,
            }
            trace.append(current)

        elif step_type == "critic":
            # Attach critic feedback to the current block (or create one if missing)
            feedback = step.get("feedback") or step.get("critique") or {}
            if current is None:
                current = {
                    "iteration": current_iteration,
                    "draft": last_draft,
                    "critic": None,
                    "edited": None,
                }
                trace.append(current)
            current["critic"] = feedback

        elif step_type == "editor":
            # Editor produces an improved draft and increments iteration
            edited_text = step.get("content", "")
            new_iter = step.get("iteration", current_iteration + 1)

            # Ensure we have a current block to attach "edited"
            if current is None:
                current = {
                    "iteration": current_iteration,
                    "draft": last_draft,
                    "critic": None,
                    "edited": None,
                }
                trace.append(current)

            current["edited"] = edited_text

            # Prepare next cycle block: draft becomes the edited text
            last_draft = edited_text
            current_iteration = new_iter

            current = {
                "iteration": current_iteration,
                "draft": last_draft,
                "critic": None,
                "edited": None,
            }
            trace.append(current)

        else:
            # Unknown step type -> ignore safely
            continue

    # Remove trailing empty block if it has no critic and no edited (can happen in edge cases)
    while trace and (trace[-1].get("critic") is None and trace[-1].get("edited") is None):
        trace.pop()

    iterations = int(final_state.get("iteration", 0))
    max_iter_final = int(final_state.get("max_iterations", max_iterations))
    quality_passed = bool(final_state.get("quality_passed", False))

    stopped_by = "passed" if (quality_passed and iterations < max_iter_final) else "max_iterations"

    return {
        "final_text": final_state.get("draft", ""),
        "iterations": iterations,
        "stopped_by": stopped_by,
        "trace": trace,
        "raw_history": raw_history,
    }
