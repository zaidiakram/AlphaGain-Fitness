from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from logger import log_message
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    log_message("❌ GOOGLE_API_KEY is missing from .env or environment.")
    raise ValueError("Missing API key")


try:
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    log_message("✅ Gemini model loaded successfully.")
except Exception as e:
    log_message(f"❌ Failed to initialize Gemini model: {e}")
    raise e

        
workout_prompt = PromptTemplate(
    input_variables=["fitness_level", "goal", "gender", "duration", "available_equipment", "age"],
    template="""
You are an AI fitness coach. Create a personalized, workout plan for the following user:

- Fitness Level: {fitness_level}
- Goal: {goal}
- Gender: {gender}
- Age: {age}
- Time Available per Day: {duration}
- Available Equipment: {available_equipment}

Include warm-up, main workout, and cooldown. Ensure the intensity matches the user's fitness level. 
Include rest days, recovery tips, and suggest alternatives if equipment is limited.
Output should be organized, easy to follow, and motivating.
"""
)


def generate_workout_plan(fitness_level,goal, gender, age, duration,available_equipment):
    prompt=workout_prompt.format(
        fitness_level=fitness_level,
        goal=goal,
        gender=gender,
        age=age,
        duration=duration,
        available_equipment=available_equipment
        
    )
    
    try:
        response = model.invoke(prompt)
        log_message("✅ Workout plane generated successfully!")
        return response
    except Exception as e:
     log_message(f"❌ Failed to generate workout plan: {str(e)}")
     return f"Error: {str(e)}"
        
if __name__ == "__main__":
    test_workout = generate_workout_plan(
        fitness_level="beginner",
        goal="weight loss",
        gender="male",
        age="25",
        duration="30",
        available_equipment="bodyweight"
    )
    print("\n📋 Generated Workout Plan:\n")
    print(test_workout.content)

