from __future__ import annotations

from app.models import Language


HINDI_MARKERS = ("नमस्ते", "डॉक्टर", "अपॉइंटमेंट", "कल", "आज", "रद्द", "बदल", "बुक")
TAMIL_MARKERS = ("வணக்கம்", "மருத்துவர்", "நாளை", "இன்று", "ரத்து", "மாற்ற", "புக்")


def detect_language(text: str, fallback: Language = Language.ENGLISH) -> Language:
    lowered = text.lower()
    if any(marker in text for marker in HINDI_MARKERS) or any(
        token in lowered for token in ("namaste", "kal", "aaj", "doctor saab")
    ):
        return Language.HINDI
    if any(marker in text for marker in TAMIL_MARKERS) or any(
        token in lowered for token in ("vanakkam", "naalai", "indru", "maruthuva")
    ):
        return Language.TAMIL
    if lowered.strip():
        return Language.ENGLISH
    return fallback


def localize(key: str, language: Language, **kwargs: object) -> str:
    messages = {
        "ask_slot": {
            Language.ENGLISH: "Which doctor and time would you prefer?",
            Language.HINDI: "आप किस डॉक्टर और समय को पसंद करेंगे?",
            Language.TAMIL: "எந்த மருத்துவர் மற்றும் எந்த நேரம் வேண்டும்?",
        },
        "booked": {
            Language.ENGLISH: "Done, I booked {doctor} for {time}.",
            Language.HINDI: "हो गया, मैंने {time} पर {doctor} के साथ अपॉइंटमेंट बुक कर दिया है।",
            Language.TAMIL: "சரி, {time}க்கு {doctor} உடன் சந்திப்பை பதிவு செய்துவிட்டேன்.",
        },
        "cancelled": {
            Language.ENGLISH: "I cancelled your appointment.",
            Language.HINDI: "मैंने आपकी अपॉइंटमेंट रद्द कर दी है।",
            Language.TAMIL: "உங்கள் சந்திப்பை ரத்து செய்துவிட்டேன்.",
        },
        "alternatives": {
            Language.ENGLISH: "That slot is not available. I can offer {options}.",
            Language.HINDI: "वह समय उपलब्ध नहीं है। मैं {options} दे सकता हूं।",
            Language.TAMIL: "அந்த நேரம் கிடைக்கவில்லை. {options} கிடைக்கிறது.",
        },
        "declined": {
            Language.ENGLISH: "No problem. I have noted that you do not want a call back now.",
            Language.HINDI: "ठीक है। मैंने नोट कर लिया है कि अभी आपको कॉल बैक नहीं चाहिए।",
            Language.TAMIL: "பரவாயில்லை. இப்போது மீண்டும் அழைப்பு வேண்டாம் என்று பதிவு செய்துள்ளேன்.",
        },
        "confirm": {
            Language.ENGLISH: "Please confirm: {doctor} at {time}?",
            Language.HINDI: "कृपया पुष्टि करें: {time} पर {doctor}?",
            Language.TAMIL: "தயவுசெய்து உறுதிப்படுத்துங்கள்: {time}க்கு {doctor}?",
        },
    }
    template = messages.get(key, messages["ask_slot"]).get(language, messages[key][Language.ENGLISH])
    return template.format(**kwargs)
