import re
from typing import Any

from agent.llm.groq_client import client, model


def _normalize_generated_tests(content: str) -> str:
    fenced_match = re.search(r"```(?:[a-zA-Z0-9_+-]+)?\n([\s\S]*?)```", content)
    if fenced_match:
        content = fenced_match.group(1)

    content = content.strip()
    lines = content.splitlines()

    if lines and re.fullmatch(r"[a-zA-Z0-9_+-]+", lines[0].strip()):
        lines = lines[1:]

    while lines and lines[0].strip().startswith("pytest "):
        lines = lines[1:]

    return "\n".join(lines).strip()


def _format_intent(intent: dict[str, Any] | None) -> str:
    """Render an intent dict for the prompt, tolerating missing fields."""
    if not isinstance(intent, dict):
        return ""

    purpose = intent.get("purpose") or ""
    properties = intent.get("properties") or []
    edge_cases = intent.get("edge_cases") or []

    if not isinstance(properties, (list, tuple)):
        properties = []
    if not isinstance(edge_cases, (list, tuple)):
        edge_cases = []

    properties_text = ", ".join(str(item) for item in properties if item is not None)
    edge_cases_text = ", ".join(str(item) for item in edge_cases if item is not None)
    purpose_text = purpose if isinstance(purpose, str) else str(purpose)

    if not any([purpose_text.strip(), properties_text, edge_cases_text]):
        return ""

    return f"""
Purpose:
{purpose_text}

Properties:
{properties_text}

Edge Cases:
{edge_cases_text}
"""


def generate_tests(
    diff: str | None,
    context: list[str] | None = None,
    intent: dict[str, Any] | None = None,
) -> str:
    if not diff or not diff.strip():
        return "Error generating tests: diff is required"

    context_text = ""
    if context:
        context_text = "\n\n".join(
            str(chunk) for chunk in context[:5]
        )  # Include only the first 5 chunks for context

    intent_text = _format_intent(intent)

    prompt = f"""
    You are a senior software engineer.
    Generate concise pytest test cases using the code diff, repository context,
    and inferred intent when they are available.

    STRICT RULES:
    - Output only valid Python pytest test code for tests/test_generated.py
    - Max  5 test functions
    - keep tests short
    - Focus on edge cases and core logic
    - NO explanations, NO extra text
    - NO markdown code fences
    - NO shell commands (for example: pytest tests/test_generated.py)


    ---INTENT---
    {intent_text}

    ---CONTEXT---
    {context_text}

    ---DIFF---
    {diff}
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from model")
        return _normalize_generated_tests(content)
    except Exception as e:
        return f"Error generating tests: {str(e)}"
    
