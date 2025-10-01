import requests

API_KEY = ""  # thay bằng key thật
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Vietnamese": "vi",
    "French": "fr",
    "Japanese": "ja",
    "Chinese": "zh"
}

CONTEXTS = ["General", "Study", "Technical", "Travel", "Work", "Gaming"]

def generate_prompt(context, src_lang, tgt_lang, text):
    if src_lang == "Auto Detect":
        src_lang = "the detected source language"

    if context == "General":
        return f"Translate the following text from {src_lang} to {tgt_lang}, keeping the meaning natural and accurate:\n{text}"
    elif context == "Study":
        return f"Translate the following text from {src_lang} to {tgt_lang} in an educational context, making it clear and easy for students to understand:\n{text}"
    elif context == "Technical":
        return f"Translate the following text from {src_lang} to {tgt_lang} in a technical context, keeping the translation precise and using correct technical terms:\n{text}"
    elif context == "Travel":
        return f"Translate the following text from {src_lang} to {tgt_lang} in a travel context, making it sound natural and conversational as if used by a traveler:\n{text}"
    elif context == "Work":
        return f"Translate the following text from {src_lang} to {tgt_lang} in a professional/business context, using polite and formal language:\n{text}"
    elif context == "Gaming":
        return f"Translate the following text from {src_lang} to {tgt_lang} in a gaming context (FPS voice chat), keeping it short, natural, and using gamer slang if appropriate:\n{text}"
    else:
        return f"Translate the following text from {src_lang} to {tgt_lang}:\n{text}"


def translate_with_gemini(prompt):
    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(API_URL, headers=headers, params=params, json=data)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {e}"
