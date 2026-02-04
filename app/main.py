import argparse
import sys
import os

# Add project root to sys path to allow running as module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.service import run_text_editor_agent
from app.report import save_report

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

    print("\n[START] Initializing Agent...")
    
    # Use Service Layer
    result = run_text_editor_agent(args.task, args.mode, user_text, args.max_iterations)
    
    # Output
    print("\n" + "="*40)
    print("FINAL TEXT")
    print("="*40)
    print(result["final_text"])
    print("="*40)
    print(f"Iterations: {result['iterations']} | Reason: {result['stopped_by']}")
    
    # Save Report
    if args.report:
        save_report(result["raw_history"], args.report)
        
    if args.verbose:
        # Use refined trace for prettier output
        for item in result["trace"]:
             print(f"\n--- Iteration {item['iteration']} ---")
             print(f"Draft Preview: {item.get('draft', '')[:50]}...")
             if 'critic' in item:
                 c = item['critic']
                 print(f"Critique: Passed={c.get('passed')} Score={c.get('score')}")
             if 'edited' in item:
                 print(f"Edited Preview: {item.get('edited', '')[:50]}...")

if __name__ == "__main__":
    main()
