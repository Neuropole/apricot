from groq import Groq 
from dotenv import load_dotenv
import os
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def generate_review(diff: str) -> str:
    from agent.llm.prompts import REVIEW_PROMPT
    prompt = REVIEW_PROMPT.format(diff=diff[:8000]) #to avoid too long input
    response = client.chat.completions.create(
        model = "llama3-70b-8192",
        messages = [
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content 
