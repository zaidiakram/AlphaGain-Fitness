import io
import time
import logging
from datetime import datetime

from fpdf import FPDF
from langchain_google_genai import ChatGoogleGenerativeAI

from logger import log_message
from config import FALLBACK_MODELS, GEMINI_TEMPERATURE, CHAT_CONTEXT_LIMIT
from workout_generate import generate_workout_plan, api_key

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
_log = logging.getLogger(__name__)

def generate_workout(fitness_level, goal, duration, equipment, gender, age):
    """
    Returns (True,  plan_text)  on success
            (False, error_msg)  on failure

    Fallback chain is handled inside workout_generate.py.
    If all models fail → error_msg = user-friendly quota message.
    """
    _log.info(f"Generating plan | {fitness_level} | {goal} | age={age} | {duration}min")

    try:
        plan = generate_workout_plan(
            fitness_level=fitness_level,
            goal=goal,
            gender=gender,
            age=age,
            duration=duration,
            available_equipment=equipment,
        )

        if hasattr(plan, "content"):
            plan = plan.content

        if "Warm-up" in plan:
            plan = plan[plan.index("Warm-up"):]

        _log.info("Plan generated successfully")
        return True, plan

    except Exception as e:
        _log.error(f"generate_workout failed: {e}")
        return False, str(e)  



def ask_fitness_coach(user_message: str, chat_history: list) -> tuple:
    """
    Sends user message + recent chat history to Gemini.
    Uses same fallback chain — tries next model on 429.

    Returns (True,  reply_text)  on success
            (False, error_msg)   on failure

    To change AI behaviour → edit the prompt string below.
    """
    _log.info(f"Chat: {user_message[:60]}")

   
    history_text = ""
    for msg in chat_history[-CHAT_CONTEXT_LIMIT:]:
        role = "User" if msg["role"] == "user" else "Coach"
        history_text += f"{role}: {msg['content']}\n"

    # ── Chat prompt ──
    prompt = f"""You are AlphaGain, a friendly and expert AI fitness coach.
- If user greets (hi / hello / hey), respond ONLY: "How can I assist you with your fitness goals today?"
- Keep replies under 200 words unless a detailed plan is asked.
- Be practical, encouraging, and specific.

Conversation so far:
{history_text}
User: {user_message}
Coach:"""

    # fallback model
    for model_name in FALLBACK_MODELS:
        try:
            _log.info(f"Chat trying: {model_name}")
            model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=GEMINI_TEMPERATURE,
                google_api_key=api_key,
            )
            response = model.invoke(prompt)
            _log.info(f"Chat success: {model_name}")
            return True, response.content

        except Exception as e:
            err = str(e)
            is_quota = "429" in err or "quota" in err.lower() or "rate" in err.lower()

            if is_quota:
                _log.warning(f"Chat {model_name} quota exceeded → trying next...")
                time.sleep(3)
            else:
                _log.error(f"Chat {model_name} error: {err}")
                time.sleep(1)
            continue

   
    return False, (
        "**Daily quota reached on all free models.**\n\n"
        "- ⏳ Wait until tomorrow (resets at midnight IST)\n"
        "- 💳 Enable billing → https://console.cloud.google.com\n"
        "- 🔑 Try a different Google API key"
    )

def create_pdf(plan_text: str, meta: dict) -> io.BytesIO:
    """
    Builds PDF in memory. Returns BytesIO buffer.
    No file saved to disk — safe for Render / cloud deploy.

    Pass buffer directly to st.download_button(data=buffer).

    Bug? → garbled text = non-latin chars (replaced with '?', FPDF limit)
         → layout broken = adjust set_margins / multi_cell below
    """
    _log.info("Building PDF...")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Title
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 12, "AlphaGain - AI Workout Plan", ln=True, align="C")

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}", ln=True, align="C")
    pdf.ln(6)

   
    pdf.set_font("Arial", "B", 11)
    for k, v in meta.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", size=11)
    clean = plan_text.replace("**", "").replace("##", "").replace("# ", "")
    for line in clean.split("\n"):
        safe = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, safe)

    buf = io.BytesIO()
    buf.write(pdf.output(dest="S").encode("latin-1"))
    buf.seek(0)

    _log.info("PDF ready")
    return buf
