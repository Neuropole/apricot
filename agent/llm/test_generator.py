from agent.llm.groq_client import client, model
def generate_tests(diff:str,context:list =None, intent:dict = None)->str:
    context_text = ""
    if context:
        context_text = "\n\n".join(context[:5])  # Include only the first 5 chunks for context

    intent_text = ""
    if intent:
        properties = ", ".join(intent.get("properties", []))
        edge_cases = ", ".join(intent.get("edge_cases", []))

        intent_text = f"""
Purpose:
{intent.get("purpose", "")}

Properties:
{properties}

Edge Cases:
{edge_cases}
"""


    prompt = f"""
You are a senior software engineer.

Generate pytest test cases using:
- Code diff
- Repository context
- Function intent

STRICT RULES:
- Output ONLY Python code
- Max 5 test functions
- Keep tests short
- Focus on edge cases and properties
- NO explanations
- NO markdown (no ```)

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
                {"role": "user", "content": prompt}
            ],
        )

        content = response.choices[0].message.content.strip()
        #cleaning the markdown if added by model
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("python"):
                content = content[len("python"):]

        return content.strip()

    except Exception as e:
        return f"Error generating tests: {str(e)}"