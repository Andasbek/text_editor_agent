from typing import TypedDict, List, Optional, Any

class AgentState(TypedDict):
    """
    Represents the state of the text editor agent.
    """
    task: str                   # The original user request
    mode: str                   # 'generate' or 'revise'
    user_text: Optional[str]    # Original text provided by user (if any)
    draft: str                  # Current version of the text
    critique: Optional[dict]    # Structured feedback from the Critic
    iteration: int              # Current iteration count
    history: List[dict]         # Log of steps for reporting
    max_iterations: int         # Configured max iterations
    # Flags
    quality_passed: bool        # Logic flag from Critic
