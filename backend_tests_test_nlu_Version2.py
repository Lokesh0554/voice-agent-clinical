from nlu.intent_parser import parse_intent

def test_english_booking():
    intent, slots = parse_intent("I want to book a checkup for Friday", "en")
    assert intent == "book_appointment"
    assert slots["day"] == "tomorrow" or "Friday"

def test_unknown():
    intent, slots = parse_intent("How is the weather?", "en")
    assert intent == "unknown"