from agent.llm.groq_client import generate_review
def generate_tests(diff:str,context:list =None)->str:
    context_text = ""
    if context:
        context_text = "\n\nContext:\n" + "\n".join(context[:5])  # Include only the first 5 chunks for context