from app.graph import verify_cycle, END

def test_verify_cycle_minimum_one_run():
    """
    If iteration is 0, must go to 'editor' even if passed is True.
    """
    state_mock = {
        "iteration": 0,
        "max_iterations": 3,
        "quality_passed": True  # Critic says it's perfect
    }
    next_node = verify_cycle(state_mock)
    assert next_node == "editor", "Should force one edit cycle even if passed initially"

def test_verify_cycle_stops_when_passed():
    """
    If iteration > 0 and passed is True, should stop.
    """
    state_mock = {
        "iteration": 1,
        "max_iterations": 3,
        "quality_passed": True
    }
    next_node = verify_cycle(state_mock)
    assert next_node == END

def test_verify_cycle_continues_when_failed():
    """
    If iteration > 0 and failed, should continue to editor.
    """
    state_mock = {
        "iteration": 1,
        "max_iterations": 3,
        "quality_passed": False
    }
    next_node = verify_cycle(state_mock)
    assert next_node == "editor"

def test_verify_cycle_stops_at_max():
    """
    If iteration >= max, should stop regardless of pass/fail.
    """
    state_mock = {
        "iteration": 3,
        "max_iterations": 3,
        "quality_passed": False
    }
    next_node = verify_cycle(state_mock)
    assert next_node == END
