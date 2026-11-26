import pytest
from agent.llm import groq_client, test_generator
from types import SimpleNamespace


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )

    @property
    def chat(self):
        return SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("```json\n{\"a\":1}\n```", '{"a":1}'),
        ("```python\nprint(\"hi\")\n```", 'print("hi")'),
        ("no fence", "no fence"),
        ("```json\n{\"key\": \"value\"}\n```", '{"key": "value"}'),
        ("```json\n{\"key\": \"value\"}", '{"key": "value"}'),
        ("```json\n{\"purpose\": \"parse ``` blocks\"}\n```", '{"purpose": "parse ``` blocks"}'),
        ("```json\n{\"purpose\": \"x\"}", '{"purpose": "x"}'),
        ("```json\n{\"purpose\": \"x"}', '{"purpose": "x"}'),
        ("```json\n{\"purpose\": \"x\"\n```", '{"purpose": "x"}'),
        ("```json\n{\"purpose\": \"x\"\n", '{"purpose": "x"}'),
    ],
)
def test_clean_json_response(content, expected):
    assert groq_client._clean_json_response(content) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("string", ["string"]),
        ("", []),
        (["a", None, "b"], ["a", "b"]),
        (("x", "y"), ["x", "y"]),
        (42, []),
        (None, []),
        (["  "], []),
    ],
)
def test_as_str_list_various_inputs(input_value, expected):
    assert groq_client._as_str_list(input_value) == expected


@pytest.mark.parametrize(
    ("intent", "expected"),
    [
        ({"purpose": None, "properties": None, "edge_cases": "input"}, {"purpose": "", "properties": [], "edge_cases": ["input"]}),
        ({"purpose": 123, "properties": [1, None], "edge_cases": None}, {"purpose": "123", "properties": ["1"], "edge_cases": []}),
        ("invalid", groq_client.EMPTY_INTENT),
    ],
)
def test_normalize_intent_sanitization(intent, expected):
    result = groq_client._normalize_intent(intent)
    assert result == expected
    # Ensure fresh lists
    result["properties"].append("leak")
    assert result["properties"] != groq_client.EMPTY_INTENT["properties"]


def test_generate_tests_empty_diff_returns_error():
    fake = FakeClient("def test_ok():\n    assert True")
    test_generator.client = fake
    assert test_generator.generate_tests("") == "Error generating tests: diff is required"
    assert not fake.calls


def test_generate_tests_intent_and_context(monkeypatch):
    fake = FakeClient("def test_ok():\n    assert True")
    monkeypatch.setattr(test_generator, "client", fake)

    context = [f"chunk{i}" for i in range(10)]
    intent = {"purpose": "add", "properties": ["commutative"], "edge_cases": ["negative"]}

    result = test_generator.generate_tests("+ def f(): return 1", context=context, intent=intent)
    assert result == "def test_ok():\n    assert True"

    prompt = fake.calls[0]["messages"][0]["content"]
    # Context should be truncated to first 5 chunks
    for i in range(5):
        assert f"chunk{i}" in prompt
    for i in range(5, 10):
        assert f"chunk{i}" not in prompt
    # Intent fields should be present
    assert "Purpose:" in prompt
    assert "add" in prompt
    assert "commutative" in prompt
    assert "negative" in prompt
    # Diff placeholder
    assert "+ def f(): return 1" in prompt
    # No trailing error
    assert not result.startswith("Error generating tests:")