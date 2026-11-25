from types import SimpleNamespace

import pytest

from agent.llm import groq_client, test_generator


def _response(content):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.calls = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return _response(self.content)


def _use_intent_client(monkeypatch, content):
    fake = FakeClient(content)
    monkeypatch.setattr(groq_client, "client", fake)
    return fake


def _use_test_client(monkeypatch, content):
    fake = FakeClient(content)
    monkeypatch.setattr(test_generator, "client", fake)
    return fake


@pytest.mark.parametrize("diff", [None, "", "   \n"])
def test_infer_intent_without_diff_returns_empty_intent(monkeypatch, diff):
    fake = _use_intent_client(monkeypatch, "should not be used")

    intent = groq_client.infer_intent(diff)

    assert intent == {"purpose": "", "properties": [], "edge_cases": []}
    assert fake.calls == []


def test_infer_intent_parses_fenced_json(monkeypatch):
    _use_intent_client(
        monkeypatch,
        '```json\n{"purpose": "add numbers", "properties": ["commutative"], '
        '"edge_cases": ["negative numbers"]}\n```',
    )

    intent = groq_client.infer_intent("+ def add(a, b): return a + b")

    assert intent == {
        "purpose": "add numbers",
        "properties": ["commutative"],
        "edge_cases": ["negative numbers"],
    }


def test_infer_intent_coerces_null_fields(monkeypatch):
    _use_intent_client(
        monkeypatch,
        '{"purpose": null, "properties": null, "edge_cases": "empty input"}',
    )

    intent = groq_client.infer_intent("+ def f(x): return x")

    assert intent["purpose"] == ""
    assert intent["properties"] == []
    assert intent["edge_cases"] == ["empty input"]


def test_infer_intent_reports_invalid_json(monkeypatch):
    _use_intent_client(monkeypatch, "this is not json")

    intent = groq_client.infer_intent("+ def f(x): return x")

    assert intent["purpose"] == ""
    assert intent["properties"] == []
    assert intent["edge_cases"] == []
    assert intent["error"]


def test_infer_intent_reports_empty_response(monkeypatch):
    _use_intent_client(monkeypatch, None)

    intent = groq_client.infer_intent("+ def f(x): return x")

    assert intent["error"]


@pytest.mark.parametrize("diff", [None, "", "   \n"])
def test_generate_review_without_diff_returns_message(monkeypatch, diff):
    fake = _use_intent_client(monkeypatch, "should not be used")

    result = groq_client.generate_review(diff)

    assert result == "No changes found to review."
    assert fake.calls == []


@pytest.mark.parametrize("diff", [None, "", "   \n"])
def test_generate_tests_without_diff_returns_error(monkeypatch, diff):
    fake = _use_test_client(monkeypatch, "def test_should_not_run(): pass")

    result = test_generator.generate_tests(diff)

    assert result == "Error generating tests: diff is required"
    assert fake.calls == []


def test_generate_tests_accepts_none_context_and_intent(monkeypatch):
    fake = _use_test_client(monkeypatch, "def test_ok():\n    assert True")

    result = test_generator.generate_tests("+ def f(): return 1")

    assert result == "def test_ok():\n    assert True"
    prompt = fake.calls[0]["messages"][0]["content"]
    assert "---INTENT---" in prompt
    assert "---CONTEXT---" in prompt


def test_generate_tests_includes_intent_when_present(monkeypatch):
    fake = _use_test_client(monkeypatch, "def test_ok():\n    assert True")

    test_generator.generate_tests(
        "+ def add(a, b): return a + b",
        context=["def add(a, b): return a + b"],
        intent={
            "purpose": "add numbers",
            "properties": ["commutative"],
            "edge_cases": ["negative numbers"],
        },
    )

    prompt = fake.calls[0]["messages"][0]["content"]
    assert "add numbers" in prompt
    assert "commutative" in prompt
    assert "negative numbers" in prompt


def test_generate_tests_tolerates_partial_intent(monkeypatch):
    fake = _use_test_client(monkeypatch, "def test_ok():\n    assert True")

    result = test_generator.generate_tests(
        "+ def f(): return 1",
        intent={"purpose": None, "properties": None, "edge_cases": []},
    )

    assert result == "def test_ok():\n    assert True"
    prompt = fake.calls[0]["messages"][0]["content"]
    assert "---DIFF---" in prompt


def test_generate_tests_reports_empty_model_response(monkeypatch):
    _use_test_client(monkeypatch, None)

    result = test_generator.generate_tests("+ def f(): return 1")

    assert result.startswith("Error generating tests:")


def test_clean_json_response_strips_simple_fence():
    raw = '```json\n{"purpose": "add numbers", "properties": [], "edge_cases": []}\n```'
    assert groq_client._clean_json_response(raw) == (
        '{"purpose": "add numbers", "properties": [], "edge_cases": []}'
    )


def test_clean_json_response_keeps_inner_fences():
    raw = '````\n{"purpose": "parse ``` blocks"}\n````'
    assert groq_client._clean_json_response(raw) == '{"purpose": "parse ``` blocks"}'


def test_clean_json_response_without_fence_returns_content():
    raw = '{"purpose": "x"}'
    assert groq_client._clean_json_response(raw) == raw


def test_clean_json_response_returns_content_if_fence_unclosed():
    raw = '```json\n{"purpose": "x"}'
    assert groq_client._clean_json_response(raw) == raw.strip()


def test_generate_tests_normalizes_fenced_response(monkeypatch):
    _use_test_client(monkeypatch, "```python\ndef test_ok():\n    assert True\n```")

    result = test_generator.generate_tests("+ def f(): return 1")

    assert result == "def test_ok():\n    assert True"
