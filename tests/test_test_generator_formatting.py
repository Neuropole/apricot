from agent.llm.test_generator import _normalize_generated_tests


def test_normalize_removes_fences_and_bash_header():
    raw = """```bash
pytest tests/test_generated.py
def test_empty_diff():
    assert True
```"""

    normalized = _normalize_generated_tests(raw)

    assert normalized == "def test_empty_diff():\n    assert True"


def test_normalize_keeps_plain_python_tests():
    raw = """def test_value():
    assert 1 == 1
"""

    normalized = _normalize_generated_tests(raw)

    assert normalized == "def test_value():\n    assert 1 == 1"
