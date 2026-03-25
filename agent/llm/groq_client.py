import os
from groq import Groq
from agent.config import MODEL
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = MODEL
def generate_review(diff: str) -> str:
    from agent.llm.prompts import REVIEW_PROMPT

    if not diff.strip():
        return "No changes found to review."

    prompt = REVIEW_PROMPT.format(diff=diff[:8000])

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating review: {str(e)}"

#local test for generate review function
if __name__ == "__main__":
    test_diff = """
diff --git a/app.py b/app.py
+ def add(a, b):
+     return a + b
"""

    result = generate_review(test_diff)
    print(result)
