# Very simple intent parser stub
def parse_intent(transcript, lang):
    # Stub: In production, use Rasa, LLM, or regex+keywords
    if "book" in transcript.lower():
        intent = "book_appointment"
    elif "reschedule" in transcript.lower():
        intent = "reschedule_appointment"
    elif "cancel" in transcript.lower():
        intent = "cancel_appointment"
    else:
        intent = "unknown"
    # Parse slots as a dict (very basic stub)
    slots = {
        "doctor": "Dr. Gupta",
        "time": "3 PM",
        "day": "tomorrow"
    }
    return intent, slots