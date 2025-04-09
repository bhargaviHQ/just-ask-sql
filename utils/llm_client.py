from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment variables")

client = Groq(api_key=GROQ_API_KEY)

def get_llm_response(prompt):
    # Extract just the user query from the prompt
    query_start = prompt.find("Analyze this user query and return the task type and details as a valid JSON string: '") + 74
    query_end = prompt.find("'", query_start)
    if query_start != -1 and query_end != -1:
        user_query = prompt[query_start:query_end]
        if "mongodb" in user_query.lower() or "password" in user_query.lower():
            return "Error: Sensitive data detected in prompt"
    
    full_prompt = f"{prompt}\n\nPlease format your response as a valid JSON string without any prefix."
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=512,
        temperature=0.7
    )
    return response.choices[0].message.content