import streamlit as st
from datetime import datetime

from config import *
from helpers import generate_workout, ask_fitness_coach, create_pdf

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --primary: #2563eb;
    --muted:   #6b7280;
    --border:  #e5e7eb;
    --radius:  8px;
}}

/* ── Background ── */
[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(135deg,
            rgba(10,10,20,0.82)  0%,
            rgba(15,23,42,0.75) 40%,
            rgba(30,41,59,0.70) 100%),
        url("{BG_IMAGE_URL}");
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}

[data-testid="stMain"] {{ background: transparent !important; }}
[data-testid="stMain"] > div > div {{ background: transparent !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}

/* ── All main area text — white ── */
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,
[data-testid="stMain"] h4,[data-testid="stMain"] h5,[data-testid="stMain"] h6,
[data-testid="stMain"] p,[data-testid="stMain"] li,[data-testid="stMain"] span,
[data-testid="stMain"] div,[data-testid="stMain"] label,[data-testid="stMain"] strong,
[data-testid="stMain"] em,[data-testid="stMain"] .stMarkdown,
[data-testid="stMain"] .stMarkdown *,
[data-testid="stMain"] [data-testid="stText"],
[data-testid="stMain"] [data-testid="stCaption"],
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stMain"] [data-testid="stMarkdownContainer"] * {{
    color: #ffffff !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.8);
}}
[data-testid="stMain"] hr {{ border-color: rgba(255,255,255,0.15) !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(255,255,255,0.07);
    border-radius: 10px 10px 0 0;
    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
    padding: 4px 8px 0;
    backdrop-filter: blur(12px);
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 500;
    font-size: 14px;
    color: rgba(241,245,249,0.65) !important;
}}
.stTabs [aria-selected="true"] {{
    color: #60a5fa !important;
    border-bottom: 2px solid #60a5fa !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: rgba(5,10,25,0.78);
    border: 1px solid rgba(255,255,255,0.12);
    border-top: none;
    border-radius: 0 0 12px 12px;
    backdrop-filter: blur(20px);
    padding: 24px !important;
}}
.stTabs [data-baseweb="tab-panel"] *:not(button):not(input) {{
    color: #ffffff !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.7);
}}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: var(--radius);
    padding: 18px;
    text-align: center;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    backdrop-filter: blur(10px);
}}
[data-testid="stMetricLabel"] {{
    font-size: 12px !important;
    color: rgba(148,163,184,1) !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #f1f5f9 !important;
    white-space: normal !important;
    word-break: break-word !important;
}}

/* ── Expanders ── */
[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: var(--radius);
    backdrop-filter: blur(10px);
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {{ color: #e2e8f0 !important; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    background: rgba(30,41,59,0.75) !important;
    border-color: rgba(96,165,250,0.35) !important;
    color: #e2e8f0 !important;
    backdrop-filter: blur(8px);
    border-radius: var(--radius);
}}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background: rgba(15,23,42,0.65) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: var(--radius);
    backdrop-filter: blur(12px);
}}
[data-testid="stChatMessage"] p {{ color: #e2e8f0 !important; }}

/* ── Chat input ── */
[data-testid="stChatInput"] {{ all: unset !important; display: block !important; }}
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div,
[data-testid="stChatInput"] > div > div > div > div {{
    background: rgba(10,15,30,0.88) !important;
    background-color: rgba(10,15,30,0.88) !important;
    border-color: rgba(255,255,255,0.18) !important;
    box-shadow: none !important;
}}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:hover,
[data-testid="stChatInput"] textarea:active,
[data-testid="stChatInputTextArea"],
.stChatInput textarea {{
    background: rgba(10,15,30,0.88) !important;
    background-color: rgba(10,15,30,0.88) !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    opacity: 1 !important;
    caret-color: #f1f5f9 !important;
}}
[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {{
    color: rgba(241,245,249,0.45) !important;
    -webkit-text-fill-color: rgba(241,245,249,0.45) !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: rgba(10,15,30,0.88) !important;
    border-right: 1px solid rgba(255,255,255,0.10);
    backdrop-filter: blur(20px);
}}
[data-testid="stSidebar"] * {{ color: #e2e8f0 !important; }}
[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] {{
    font-weight: 500;
    font-size: 13px;
    margin-bottom: 2px !important;
    color: #94a3b8 !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: #f1f5f9 !important; }}

/* Sidebar selectbox */
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput input {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: var(--radius);
    font-size: 14px;
    color: #f1f5f9 !important;
}}

/* Sidebar number input */
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div {{
    background: rgba(10,15,30,0.88) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    overflow: hidden !important;
    width: 100%;
}}
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div > div,
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div > div > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] [data-testid="stNumberInput"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input:hover {{
    background: transparent !important;
    background-color: transparent !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 14px !important;
    opacity: 1 !important;
}}
[data-testid="stSidebar"] [data-testid="stNumberInput"] button,
[data-testid="stSidebar"] [data-testid="stNumberInput"] button:hover {{
    background: transparent !important;
    background-color: transparent !important;
    color: #f1f5f9 !important;
    border: none !important;
    box-shadow: none !important;
}}

/* Sidebar compact spacing */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
    margin-bottom: 6px !important;
}}
[data-testid="stSidebar"] [data-testid="stSlider"] {{
    margin-top: -4px !important;
    margin-bottom: 6px !important;
}}
[data-testid="stSlider"] div[data-baseweb="slider"] > div {{ height: 4px; }}

/* ── Buttons ── */
.stButton > button {{
    background: var(--primary);
    color: white !important;
    font-weight: 600;
    font-size: 14px;
    border: none;
    border-radius: var(--radius);
    padding: 10px 16px;
    width: 100%;
    transition: 0.2s ease;
}}
.stButton > button:hover {{ background: #1d4ed8; }}

.stDownloadButton > button {{
    background: rgba(255,255,255,0.08);
    color: #60a5fa !important;
    border: 1px solid #3b82f6 !important;
    border-radius: var(--radius);
    font-weight: 600;
    backdrop-filter: blur(8px);
}}
.stDownloadButton > button:hover {{ background: rgba(59,130,246,0.15); }}

/* ── Spinner ── */
[data-testid="stSpinner"] p {{ color: #94a3b8 !important; }}
</style>
""", unsafe_allow_html=True)


if "workout_history" not in st.session_state:
    st.session_state.workout_history = []  

if "current_plan" not in st.session_state:
    st.session_state.current_plan = None    

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []     


def main():

    with st.sidebar:
        st.header("📝 Input Your Details")

        fitness_level = st.selectbox("Fitness Level",             FITNESS_LEVELS)
        goal          = st.selectbox("Fitness Goal",              GOAL_OPTIONS)
        gender        = st.selectbox("Gender",                    GENDER_OPTIONS)
        age           = st.number_input("Age",                    min_value=AGE_MIN,  max_value=AGE_MAX,  value=AGE_DEFAULT,  step=1)
        duration      = st.number_input("Workout Duration (in minutes)", min_value=DUR_MIN, max_value=DUR_MAX, value=DUR_DEFAULT, step=DUR_STEP)
        equipment     = st.selectbox("Available Equipment",       EQUIPMENT_OPTIONS)
        generate_btn  = st.button("🚀 Generate Workout Plan",     use_container_width=True)

    
    st.title("⚡ AlphaGain — AI Workout Planner")
    st.caption("Generate a personalized workout plan and chat with your AI fitness coach.")
    st.divider()

    tab_plan, tab_chat, tab_history = st.tabs([
        "📋 Workout Plan",
        "💬 Fitness Chat",
        "📚 History",
    ])

   
    with tab_plan:

        if generate_btn:
            with st.spinner("Generating your workout plan..."):
                success, result = generate_workout(
                    fitness_level, goal, duration, equipment, gender, age
                )

            if not success:
              
                st.error("Could not generate your plan.")
                st.markdown(result)
            else:
                entry = {
                    "plan"          : result,
                    "fitness_level" : fitness_level,
                    "goal"          : goal,
                    "duration"      : duration,
                    "equipment"     : equipment,
                    "gender"        : gender,
                    "age"           : age,
                    "date"          : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                st.session_state.workout_history.append(entry)
                st.session_state.current_plan = entry
                st.success("Workout plan generated successfully!")

        plan = st.session_state.current_plan

        if plan:
        
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Fitness Level", plan["fitness_level"])
            c2.metric("Duration",      f"{plan['duration']} min")
            c3.metric("Goal",          plan["goal"])
            c4.metric("Equipment",     plan["equipment"])

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(plan["plan"])
            st.markdown("<br>", unsafe_allow_html=True)

         
            pdf_buf = create_pdf(plan["plan"], {
                "Fitness Level" : plan["fitness_level"],
                "Goal"          : plan["goal"],
                "Gender"        : plan["gender"],
                "Age"           : str(plan["age"]),
                "Duration"      : f"{plan['duration']} minutes",
                "Equipment"     : plan["equipment"],
            })
            st.download_button(
                label               = "⬇️ Download as PDF",
                data                = pdf_buf,
                file_name           = f"AlphaGain_Workout_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime                = "application/pdf",
                use_container_width = True,
            )
        else:
            st.info("👈 Fill in your profile in the sidebar and click **Generate Workout Plan** to get started.")


    with tab_chat:
        st.subheader("💬 Ask your AI Fitness Coach")
        st.caption("Ask anything about workouts, nutrition, recovery, or your plan.")

      
        for msg in st.session_state.chat_history:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg["content"])

      
        if user_input := st.chat_input("Ask a fitness question..."):
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    ok, reply = ask_fitness_coach(user_input, st.session_state.chat_history)
                if ok:
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "ai", "content": reply})
                else:
                    st.warning(reply)

      
        if st.session_state.chat_history:
            if st.button("🗑️ Clear conversation"):
                st.session_state.chat_history = []
                st.rerun()

    
    with tab_history:
        if st.session_state.workout_history:
            st.subheader("Past Workout Plans")

         
            for i, entry in enumerate(reversed(st.session_state.workout_history)):
                label = f"📅 {entry['date']}  ·  {entry['goal']}  ·  {entry['fitness_level']}"
                with st.expander(label):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**Gender:** {entry['gender']}")
                    c2.write(f"**Age:** {entry['age']}")
                    c3.write(f"**Duration:** {entry['duration']} min")
                    c4.write(f"**Equipment:** {entry['equipment']}")
                    st.markdown("---")
                    st.write(entry["plan"])

                
                    if st.button("Load this plan", key=f"load_{i}"):
                        st.session_state.current_plan = entry
                        st.success("Plan loaded! Switch to the Workout Plan tab.")
        else:
            st.info("No workout history yet. Generate your first plan to see it here.")


if __name__ == "__main__":
    main()
