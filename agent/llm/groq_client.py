import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from agent.config import MODEL

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = MODEL

EMPTY_INTENT: dict[str, Any] = {
    "purpose": "",
    "properties": [],
    "edge_cases": [],
}
def generate_review(diff: str,context : list = None) -> str:
    from agent.llm.prompts import REVIEW_PROMPT

    if not diff.strip():
        return "No changes found to review."

    # prompt = REVIEW_PROMPT.format(diff=diff[:8000])
    MAX_CONTEXT_CHARS = 5000
    
    '''preparing context'''
    context_text = ""
    if context:
        combined = "\n\n".join(context) # Include up to 5 context items(limitting)
        context_text = combined[:MAX_CONTEXT_CHARS]
    prompt = f"""
    You are an AI code reviewer. Use the provided repository context (if available) to give better insights.

    ---CONTEXT---
    {context_text}

    ---DIFF---
    {diff[:8000]} 

    ---TASK---
    {REVIEW_PROMPT}
    
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating review: {str(e)}"


def _clean_json_response(content: str) -> str:
    """Strip an optional markdown code fence from a model response."""
    content = content.strip()
    fenced_match = re.search(r"```(?:[a-zA-Z0-9_+-]+)?\n([\s\S]*?)```", content)
    if fenced_match:
        content = fenced_match.group(1)
    return content.strip()


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if item is not None]
    return []


def _normalize_intent(intent: Any) -> dict[str, Any]:
    """Coerce an arbitrary model response into the expected intent shape."""
    if not isinstance(intent, dict):
        return dict(EMPTY_INTENT)

    purpose = intent.get("purpose") or ""
    normalized: dict[str, Any] = {
        "purpose": purpose if isinstance(purpose, str) else str(purpose),
        "properties": _as_str_list(intent.get("properties")),
        "edge_cases": _as_str_list(intent.get("edge_cases")),
    }
    if intent.get("error"):
        normalized["error"] = str(intent["error"])
    return normalized


def infer_intent(diff: str | None) -> dict[str, Any]:
    """Extract the purpose, invariants, and edge cases of a diff.

    Returns an empty intent when there is nothing to analyze, and an intent
    carrying an ``error`` key when the model response cannot be used.
    """
    from agent.llm.prompts import INTENT_PROMPT

    if not diff or not diff.strip():
        return dict(EMPTY_INTENT)

    prompt = INTENT_PROMPT.replace("{diff}", diff[:8000])

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from model")
        return _normalize_intent(json.loads(_clean_json_response(content)))
    except Exception as e:
        return {**EMPTY_INTENT, "error": str(e)}


#local test for generate review function
if __name__ == "__main__":
    test_diff = """
diff --git a/app.py b/app.py
+ def divide(a, b):
+     return a / b
"""

    test_context = [
        "def safe_divide(a, b): return a / b if b != 0 else 0",
        "Utility functions for math operations"
    ]

    result = generate_review(test_diff, context=test_context) #added conetxt parameter (kindly see @pleasingsunlight)
    print(result)