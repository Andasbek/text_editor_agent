# report.py
import json
import os
from typing import List, Any

def save_report(history: List[dict], filename: str = "report.json"):
    """
    Saves the agent's history steps to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"\n[INFO] Report saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save report: {e}")

def print_step_summary(step_data: dict):
    """
    Prints a readable summary of a step to the console.
    """
    step_type = step_data.get("step")
    
    if step_type == "writer":
        print("\n--- [WRITER] Draft Generated ---")
        # Preview first 100 chars
        content = step_data.get("content", "")
        preview = (content[:100] + '...') if len(content) > 100 else content
        print(f"Content: {preview}\n")
        
    elif step_type == "critic":
        print("\n--- [CRITIC] Reviewing ---")
        fb = step_data.get("feedback", {})
        passed = fb.get("passed", False)
        score = fb.get("score", 0.0)
        print(f"Passed: {passed} | Score: {score}")
        if not passed:
            issues = fb.get("issues", [])
            print(f"Issues: {len(issues)} found")
            
    elif step_type == "editor":
        print("\n--- [EDITOR] Improving Text ---")
        iteration = step_data.get("iteration")
        print(f"Iteration: {iteration}")
