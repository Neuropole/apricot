import os
from groq import Groq
from agent.config import MODEL
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = MODEL
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

def infer_intent(diff: str) -> dict:
    from agent.llm.prompts import INTENT_PROMPT
    import json

    prompt  = INTENT_PROMPT.format(diff=diff[:8000])
    try:
        response = client.chat.completions.create(
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        content = response.choices[0].message.content.strip()

        #cleaning the markdown if added by model
        if content.startswith("```"):
            content = content.split("```")[1]  # Extract code from markdown
            if content.startswith("json"):
                content = content[len("json"):]  # Remove language specifier    
        return json.loads(content)
    except Exception as e:
        return {
            "purpose": "",
            "properties": [],
            "edge_cases": [],
            "error": str(e)

        }

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

