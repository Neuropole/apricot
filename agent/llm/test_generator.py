from agent.llm.groq_client import client, model
def generate_tests(diff:str,context:list =None)->str:
    context_text = ""
    if context:
        context_text = "\n\n".join(context[:5])  # Include only the first 5 chunks for context
    prompt = f"""
    You are a senior software engineer.
    Generate concise pytest test cases for the given code diff.

    STRICT RULES:
    - Output only code
    - Max  5 test functions
    - keep tests short
    - Focus on edge cases and core logic
    - NO explanations, NO extra text


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
        if content.startswith("```"):
            content = content.split("```")[1]  # Extract code from markdown
            if content.startswith("python"):
                content = content[len("python"):]  # Remove language specifier
        return content.strip()
    except Exception as e:
        return f"Error generating tests:{str(e)}"
    