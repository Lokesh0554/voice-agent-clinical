# Stub logic for appointment scheduling
def handle_appointment(intent, slots, session_memory):
    if intent == "book_appointment":
        response = f"Confirmed appointment with {slots['doctor']} at {slots['time']} on {slots['day']}."
        trace = f"Intent: {intent}, slots: {slots}"
    elif intent == "reschedule_appointment":
        response = "Your appointment has been rescheduled."
        trace = f"Intent: {intent}, slots: {slots}"
    elif intent == "cancel_appointment":
        response = "Your appointment has been cancelled."
        trace = f"Intent: {intent}, slots: {slots}"
    else:
        response = "Sorry, I did not understand. Can you repeat?"
        trace = "Unknown intent."
    return response, trace