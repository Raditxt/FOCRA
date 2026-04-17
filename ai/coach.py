import ollama
from ai.prompts import SYSTEM_PROMPT, build_analysis_prompt
from config.settings import OLLAMA_MODEL, OLLAMA_HOST


def get_coaching_insight(context: str, user_name: str) -> str:
    client = ollama.Client(host=OLLAMA_HOST)
    prompt = build_analysis_prompt(context, user_name)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.message.content