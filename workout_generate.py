import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from logger import log_message
from config import FALLBACK_MODELS, GEMINI_TEMPERATURE

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    log_message("GOOGLE_API_KEY is missing from .env", "error")
    raise ValueError("GOOGLE_API_KEY missing — add it to your .env file")

_prompt = PromptTemplate(
    input_variables=["fitness_level", "goal", "gender", "duration", "available_equipment", "age"],
    template="""
You are a professional fitness coach.

Create a personalized workout plan for:

Fitness Level: {fitness_level}
Goal: {goal}
Gender: {gender}
Age: {age}
Workout Duration: {duration} minutes
Available Equipment: {available_equipment}

Include:
- Warm-up
- Main workout
- Cooldown
- Weekly schedule
- Recovery tips
- Progression suggestions

Do NOT include any motivational conclusion paragraph.
Keep the response structured and professional.
"""
)


#  Helper:
def _make_model(model_name: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=GEMINI_TEMPERATURE,
        google_api_key=api_key,
    )

def generate_workout_plan(fitness_level, goal, gender, age, duration, available_equipment):
    """
    Calls Gemini with fallback chain. Tries each model in order.

    Returns:
        LangChain response object (.content = plan text)  on success
        raises Exception with user-friendly message        if ALL fail

    Flow:
        model 1 → 429 → 3s wait → model 2 → 429 → 3s wait → model 3 → 429 → raise
    """
    formatted_prompt = _prompt.format(
        fitness_level=fitness_level,
        goal=goal,
        gender=gender,
        age=age,
        duration=duration,
        available_equipment=available_equipment,
    )

    for model_name in FALLBACK_MODELS:
        try:
            log_message(f"Trying model: {model_name}")
            response = _make_model(model_name).invoke(formatted_prompt)
            log_message(f"Success with: {model_name}")
            return response

        except Exception as e:
            err = str(e)
            is_quota = "429" in err or "quota" in err.lower() or "rate" in err.lower()

            if is_quota:
                log_message(f"{model_name} quota exceeded → trying next...", "warning")
                time.sleep(3)
            else:
                log_message(f"{model_name} error: {err}", "error")
                time.sleep(1)
            continue  

    log_message("All models quota exceeded", "error")
    raise Exception(
        "**Daily quota reached on all free models.**\n\n"
        "- ⏳ Wait until tomorrow (resets at midnight IST)\n"
        "- 💳 Enable billing → https://console.cloud.google.com\n"
        "- 🔑 Try a different Google API key"
    )

if __name__ == "__main__":
    result = generate_workout_plan(
        fitness_level="Beginner", goal="Weight Loss",
        gender="Male", age="25", duration="30",
        available_equipment="Bodyweight",
    )
    print(result.content)
