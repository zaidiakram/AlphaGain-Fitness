import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime

# Load environment variables
load_dotenv()

# Fetch API Key from .env file
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE API Key missing! Please add it to the .env file.")
    st.stop()

# Initialize Gemini model
try:
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
except Exception as e:
    st.error(f"❌ GOOGLE Initialization Error: {str(e)}")
    st.stop()

# Define prompt template
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

# Function to generate workout
def generate_workout(fitness_level, goal, duration, equipment, gender, age):
    prompt = workout_prompt.format(
        fitness_level=fitness_level,
        goal=goal,
        gender=gender,
        age=age,
        duration=duration,
        available_equipment=equipment,
    )
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to create PDF
def create_pdf(workout_plan, fitness_level, goal, duration, equipment):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Personalized Workout Plan", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fitness Level: {fitness_level}", ln=True)
    pdf.cell(200, 10, txt=f"Goal: {goal}", ln=True)
    pdf.cell(200, 10, txt=f"Duration: {duration} minutes", ln=True)
    pdf.cell(200, 10, txt=f"Equipment: {equipment}", ln=True)
    pdf.ln(10)
    
    pdf.multi_cell(0, 10, workout_plan)
    
    filename = f"Workout_Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# MAIN Streamlit Frontend
def main():
    # Custom CSS Styling
    st.markdown("""
        <style>
        body {
            background-color: #f7f9fc;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton>button {
            background-color: #2e8b57;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stSelectbox, .stNumberInput, .stTextInput {
            background-color: white;
            border-radius: 10px;
        }
        h1 {
            text-align: center;
            color: #1f3b4d;
        }
        .block-container {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏋️‍♂️AlphaGain:-Workout Planner")
    st.markdown("Generate a custom workout plan tailored to your needs!💪")

    with st.sidebar:
        st.header("📝 Input Your Details")
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
        goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Endurance", "General Fitness"])
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=12, max_value=90, value=25, step=1)
        duration = st.number_input("Workout Duration (in minutes)", min_value=10, max_value=120, value=30, step=5)
        available_equipment = st.selectbox("Available Equipment", ["Bodyweight", "Dumbbells", "Resistance Bands", "Full Gym"])
        generate_button = st.button("🚀 Generate Workout Plan")

    if "workout_history" not in st.session_state:
        st.session_state.workout_history = []

    if generate_button:
        with st.spinner("Crafting your AI-powered workout plan..."):
            workout_plan = generate_workout(
                fitness_level=fitness_level,
                goal=goal,
                duration=duration,
                equipment=available_equipment,
                gender=gender,
                age=age
            )

            st.session_state.workout_history.append({
                "plan": workout_plan,
                "fitness_level": fitness_level,
                "goal": goal,
                "duration": duration,
                "equipment": available_equipment,
                "gender": gender,
                "age": age,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.success("✅ Your personalized workout plan is ready!")

        # Display the plan
        st.subheader("📋 Workout Plan")
        st.markdown(f"**Goal**: {goal} | **Duration**: {duration} min | **Equipment**: {available_equipment}")
        st.write(workout_plan)

        # Offer PDF download
        pdf_file = create_pdf(workout_plan, fitness_level, goal, duration, available_equipment)
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="⬇️ Download as PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )

    # History Display
    if st.session_state.workout_history:
        st.markdown("---")
        st.subheader("📚 Your Workout History")
        for i, entry in enumerate(st.session_state.workout_history):
            with st.expander(f"📅 Workout {i+1} — {entry['date']}"):
                st.write(f"**Fitness Level:** {entry['fitness_level']}")
                st.write(f"**Goal:** {entry['goal']}")
                st.write(f"**Gender:** {entry['gender']}")
                st.write(f"**Age:** {entry['age']}")
                st.write(f"**Duration:** {entry['duration']} min")
                st.write(f"**Equipment:** {entry['equipment']}")
                st.markdown("---")
                st.write(entry["plan"])

if __name__ == "__main__":
    main()
