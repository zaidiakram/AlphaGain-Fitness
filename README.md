# AlphaGain - AI Workout Planner 

AlphaGain is an AI-powered fitness app that generates personalized workout plans and provides guidance through an AI fitness coach using Google Gemini AI.

## Features

* AI-based workout plan generation
* AI fitness coach chat for guidance
* Export workout plans as PDF
* Simple and clean dark UI
* Smart fallback handles API quota limits.

## System Architecture


<img width="1184" height="388" alt="Screenshot 2026-03-12 044448" src="https://github.com/user-attachments/assets/aa082963-f736-4b6d-9888-6566959d2bf5" />


## Installation

```bash
git clone https://github.com/zaidiakram/AlphaGain-Fitness.git
cd AlphaGain-Fitness

python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

## Setup

Create a `.env` file and add:
```
GOOGLE_API_KEY=your_api_key
```
## Run the App

```bash
streamlit run app.py
```

