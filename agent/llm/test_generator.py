import re
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


def generate_tests(diff:str,context:list =None)->str:
    context_text = ""
    if context:
        context_text = "\n\n".join(context[:5])  # Include only the first 5 chunks for context
    prompt = f"""
    You are a senior software engineer.
    Generate concise pytest test cases for the given code diff.

    STRICT RULES:
    - Output only valid Python pytest test code for tests/test_generated.py
    - Max  5 test functions
    - keep tests short
    - Focus on edge cases and core logic
    - NO explanations, NO extra text
    - NO markdown code fences
    - NO shell commands (for example: pytest tests/test_generated.py)


    ---CONTEXT---
    {context_text}

    ---DIFF---
    {diff}
    """


    try:
        response = client.chat.completions.create(
            model = model,
            messages = [
                
                {
                    "role": "user",
                    "content": prompt
                }
            ],
          )
        content =response.choices[0].message.content.strip()
        return _normalize_generated_tests(content)
    except Exception as e:
        return f"Error generating tests:{str(e)}"
    
