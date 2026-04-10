from google import genai
from ai.prompts import SYSTEM_PROMPT, build_analysis_prompt
from config.settings import GEMINI_API_KEY, MODEL_NAME, MAX_TOKENS


def get_coaching_insight(context: str, user_name: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = build_analysis_prompt(context, user_name)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
    )
    return response.text