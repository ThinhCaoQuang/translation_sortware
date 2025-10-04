import os
from dataclasses import dataclass

@dataclass
class Settings:
	openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
	openai_text_model: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
	app_locale: str = os.getenv("APP_LOCALE", "vi")  # "vi" hoặc "en"
	db_path: str = os.getenv("DB_PATH", "translations.db")

settings = Settings()
