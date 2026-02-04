import argparse
import sys
import os

# Add project root to sys path to allow running as module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.graph import build_graph
from app.report import save_report, print_step_summary

def main():
    parser = argparse.ArgumentParser(description="AI Text Editor Agent")
    
    parser.add_argument("--mode", type=str, choices=["generate", "revise"], required=True, help="Operation mode")
    parser.add_argument("--task", type=str, required=True, help="Description of what to write or fix")
    parser.add_argument("--text-file", type=str, help="Path to input text file (required for revise mode)")
    parser.add_argument("--max-iterations", type=int, default=3, help="Max edit loops")
    parser.add_argument("--report", type=str, default="report.json", help="Path to save output report")
    parser.add_argument("--verbose", action="store_true", help="Print detailed step info")
    
    args = parser.parse_args()
    
    # Validation
    user_text = ""
    if args.mode == "revise":
        if not args.text_file:
            print("Error: --text-file is required for revise mode")
            sys.exit(1)
        try:
            with open(args.text_file, 'r', encoding='utf-8') as f:
                user_text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    # Init State
    initial_state = {
        "task": args.task,
        "mode": args.mode,
        "user_text": user_text,
        "draft": "",
        "critique": {},
        "iteration": 0,
        "history": [],
        "max_iterations": args.max_iterations,
        "quality_passed": False
    }
    
    print("\n[START] Initializing Agent...")
    app = build_graph()
    
    final_state = app.invoke(initial_state)
    
    # Output
    print("\n" + "="*40)
    print("FINAL TEXT")
    print("="*40)
    print(final_state["draft"])
    print("="*40)
    
    # Save Report
    if args.report:
        save_report(final_state["history"], args.report)
        
    if args.verbose:
        for step in final_state["history"]:
            print_step_summary(step)

if __name__ == "__main__":
    main()
