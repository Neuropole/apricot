import pytest

from agent.llm import groq_client, test_generator


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        # Mimic the OpenAI chat completion response structure
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )

    @property
    def chat(self):
        return SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )


class SimpleNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_clean_json_response_strips_code_fence(monkeypatch):
    content = "```json\n{\"key\": \"value\"}\n```"
    result = groq_client._clean_json_response(content)
    assert result == '{"key": "value"}'


def test_normalize_intent_handles_non_dict(monkeypatch):
    # Passing a string should return the empty intent
    result = groq_client._normalize_intent("not a dict")
    assert result == groq_client.EMPTY_INTENT
    # Passing a dict with missing keys should default correctly
    result = groq_client._normalize_intent({"purpose": None, "properties": None, "edge_cases": "input"})
    assert result["purpose"] == ""
    assert result["properties"] == []
    assert result["edge_cases"] == ["input"]


def test_format_intent_empty_returns_empty(monkeypatch):
    assert test_generator._format_intent(None) == ""
    assert test_generator._format_intent({"purpose": "", "properties": [], "edge_cases": []}) == ""


def test_generate_tests_with_intent_and_context(monkeypatch):
    fake = FakeClient("def test_ok():\n    assert True")
    monkeypatch.setattr(test_generator, "client", fake)

    intent = {"purpose": "add numbers", "properties": ["commutative"], "edge_cases": ["negative"]}
    context = ["def add(a, b): return a + b", "def sub(a, b): return a - b"]
    result = test_generator.generate_tests("+ def add(a, b): return a + b", context=context, intent=intent)

    # Normalized content should match the fake response
    assert result == "def test_ok():\n    assert True"
    # Prompt should contain intent and context markers
    prompt = fake.calls[0]["messages"][0]["content"]
    assert "---INTENT---" in prompt
    assert "add numbers" in prompt
    assert "commutative" in prompt
    assert "negative" in prompt
    assert "---CONTEXT---" in prompt
    assert "def add(a, b): return a + b" in prompt
    assert "def sub(a, b): return a - b" in prompt


def test_generate_tests_error_on_empty_diff(monkeypatch):
    fake = FakeClient("def test_ok():\n    assert True")
    monkeypatch.setattr(test_generator, "client", fake)
    result = test_generator.generate_tests(None)
    assert result == "Error generating tests: diff is required"
    assert fake.calls == []