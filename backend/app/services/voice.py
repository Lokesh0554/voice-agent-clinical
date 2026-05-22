from __future__ import annotations

from app.models import Language


class SpeechToText:
    async def transcribe(self, audio_text: str) -> str:
        return audio_text.strip()


class TextToSpeech:
    async def synthesize(self, text: str, language: Language) -> str:
        safe_lang = language.value
        return f"demo://tts/{safe_lang}/{abs(hash(text))}"
