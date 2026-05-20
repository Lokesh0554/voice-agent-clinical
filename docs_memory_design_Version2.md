# Memory Design

## Session Memory (Redis)
- Keyed by session or conversation IDs.
- Holds current intent, slots, pending confirmations, last utterances.
- TTL: 10 minutes per session (auto-cleanup).
- Used for active context during call.

## Patient Memory (Persistent, e.g. Postgres)
- Keyed by patient ID or phone number.
- Persists language preference, appointment history, prior interactions.
- Used to personalize each session, and recall context across encounters.

---

### Example (in code):

```python
# Store context during a voice session
session_memory.set(session_id, {
    'current_intent': 'book_appointment',
    'slot_state': {'doctor': 'Dr. Rao'},
}, ttl=600)

# Recall for future sessions
patient_memory.set(patient_id, {
    'language': 'hi',
    'appointments': [...],
})
```