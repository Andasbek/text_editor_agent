import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm():
    """
    Returns a MagicMock that acts like a ChatOpenAI instance.
    """
    mock = MagicMock()
    # default response
    mock.invoke.return_value = AIMessage(content="Mocked Content")
    return mock

@pytest.fixture
def mock_get_llm(mock_llm):
    """
    Patches app.nodes.get_llm to return the mock_llm.
    """
    with patch("app.nodes.get_llm", return_value=mock_llm) as p:
        yield p
