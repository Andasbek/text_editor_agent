import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm(json_mode: bool = False):
    """
    Returns an instance of ChatOpenAI.
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        # Fallback or error, but let's assume env is set or passed
        pass

    kwargs = {
        "model": model_name,
        "temperature": 0.0, # Low temp for reproducibility
    }
    
    if json_mode:
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
        
    return ChatOpenAI(**kwargs)
