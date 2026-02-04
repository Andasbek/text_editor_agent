# Text Editor Agent

An iterative, self-correcting AI text editor built with LangGraph.
The agent follows a **Writer -> Critic -> Editor** cycle to improve content quality autonomously.

## Features
- **Cyclic Refinement**: Automatically critiques and edits text.
- **Structured Feedback**: Critic passes detailed JSON feedback (issues, suggestions, score).
- **Minimum One Cycle**: detailed in specs, ensures at least one pass of editing.
- **Modes**:
  - `generate`: Create new content.
  - `revise`: Polish existing content.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env`:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
   > **Note:** The project will raise a `ValueError` if the API key is not set.

## Usage

## Usage

### Web Interface (Streamlit)
```bash
streamlit run ui/streamlit_app.py
```

### CLI


**Generate Text:**
```bash
python -m app.main --mode generate --task "Explain quantum entanglement to a 5-year old"
```

**Revise Text:**
```bash
python -m app.main --mode revise --task "Fix grammar and make concise" --text-file my_draft.txt
```

**Options:**
- `--max-iterations`: Limit the number of refines (default: 3).
- `--report`: Save JSON trace (default: report.json).
- `--verbose`: Show intermediate steps in console.

## Architecture

- **Nodes** (`app/nodes.py`): Writer, Critic, Editor.
- **Graph** (`app/graph.py`): StateGraph with conditional edging.
- **State** (`app/state.py`): TypedDict tracking the text evolution.

## Testing

Run unit tests:
```bash
pytest tests/
```