from agent.llm.groq_client import client, model
def generate_tests(diff:str,context:list =None)->str:
    context_text = ""
    if context:
        context_text = "\n\nContext:\n" + "\n".join(context[:5])  # Include only the first 5 chunks for context
    prompt = f"""
    You are a senior software engineer.
    Generate unit tests for the given code diff.

    ---CONTEXT---
    {context_text}

    ---DIFF---
    {diff}

    ---OUTPUT FORMAT---
    -Use pytest
    - cover edge cases
    - keep it concise
    """
    response = client.chat.completions.create(
        model = model,
        messages = [
            
            {
                "role": "user",
                "content": prompt
            }
        ],
      )
    return response.choices[0].message.content