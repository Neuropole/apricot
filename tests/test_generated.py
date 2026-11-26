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
    "input_value,expected",
    [
        ("string", ["string"]),
        ("", []),
        (["a", None, "b"], ["a", "b"]),
        (("x", "y"), ["x", "y"]),
        (42, []),
        (None, []),
    ],
)
def test_as_str_list_various_inputs(input_value, expected):
    result = groq_client._as_str_list(input_value)
    assert result == expected


@pytest.mark.parametrize(
    "content,expected",
    [
        ("```json\n{\"a\":1}\n```", '{"a":1}'),
        ("```python\nprint(\"hi\")\n```", 'print("hi")'),
        ("no fence", "no fence"),
        ("```json\n{\"key\": \"value\"}\n```", '{"key": "value"}'),
        ("```json\n{\"key\": \"value\"}", '{"key": "value"}'),
    ],
)
def test_clean_json_response(content, expected):
    assert groq_client._clean_json_response(content) == expected


def test_normalize_intent_missing_and_wrong_types(monkeypatch):
    intent = {"purpose": None, "properties": None, "edge_cases": "input"}
    result = groq_client._normalize_intent(intent)
    assert result["purpose"] == ""
    assert result["properties"] == []
    assert result["edge_cases"] == ["input"]
    assert groq_client._normalize_intent("invalid") == groq_client.EMPTY_INTENT


def test_generate_tests_context_truncation(monkeypatch):
    fake = FakeClient("def test_ok():\n    assert True")
    monkeypatch.setattr(test_generator, "client", fake)
    context = [f"chunk{i}" for i in range(10)]
    result = test_generator.generate_tests("+ def f(): return 1", context=context, intent=None)
    assert result == "def test_ok():\n    assert True"
    prompt = fake.calls[0]["messages"][0]["content"]
    for i in range(5):
        assert f"chunk{i}" in prompt
    for i in range(5, 10):
        assert f"chunk{i}" not in prompt


def test_generate_tests_empty_diff_error(monkeypatch):
    fake = FakeClient("def test_ok():\n    assert True")
    monkeypatch.setattr(test_generator, "client", fake)
    result = test_generator.generate_tests("")
    assert result == "Error generating tests: diff is required"
    assert fake.calls == []