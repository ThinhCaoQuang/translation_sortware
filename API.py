from typing import Optional
from openai import OpenAI
from config import settings

LANGUAGES = {
    "Auto Detect": "auto",
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Nhật": "ja",
    "Tiếng Pháp": "fr",
    "Tiếng Trung": "zh",
    "Tiếng Hàn": "ko",
    "Tiếng Đức": "de",
    "Tiếng Thái": "th",
    "Tiếng Indonesia": "id",
}

CONTEXTS = [
    "General","Medical/Healthcare","Technical/IT","Legal/Contracts",
    "Business/Work","Gaming/Entertainment","Travel/Tourism","Study/Education"
]

def _client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("Chưa đặt OPENAI_API_KEY.")
    return OpenAI(api_key=settings.openai_api_key)

def _system_prompt(src_code: str, dst_code: str, domain: Optional[str]) -> str:
    goals = [
        "You are a professional translator.",
        "Return only the translated text. No explanations.",
        "Preserve original line breaks and punctuation.",
        "Keep code snippets and URLs unchanged.",
        "If the source language is 'auto', first infer it, then translate."
    ]
    if domain and domain != "General":
        goals.append(f"Bias terminology and tone toward the domain: {domain}.")
    return "\n".join(goals) + f"\nSource language code: {src_code}. Target language code: {dst_code}."

def translate_text(
    text: str,
    src_lang_code: str = "auto",
    dst_lang_code: str = "en",
    domain: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    if not text.strip():
        return ""
    client = _client()
    model = model or settings.openai_text_model
    system = _system_prompt(src_lang_code, dst_lang_code, domain)

    resp = client.responses.create(
        model=model,
        input=[
            {"role":"system","content":[{"type":"text","text":system}]},
            {"role":"user","content":[{"type":"text","text":text}]},
        ],
        temperature=0.2,
    )
    try:
        return (resp.output_text or "").strip()
    except Exception:
        parts = []
        for item in getattr(resp, "output", []):
            if getattr(item, "type", "") == "output_text":
                parts.append(getattr(item, "text", ""))
        return "\n".join(p for p in parts if p).strip()