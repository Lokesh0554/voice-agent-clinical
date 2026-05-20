import time
from stt.recognize import stt_recognize
from nlu.intent_parser import parse_intent
from appointments.scheduler import handle_appointment
from memory.session_memory import SessionMemory
from tts.synth import tts_speak

def process_audio_pipeline(audio):
    timings = {}
    timings['stt_start'] = time.time()
    transcript, lang = stt_recognize(audio)
    timings['stt_end'] = time.time()

    timings['nlu_start'] = time.time()
    intent, slots = parse_intent(transcript, lang)
    timings['nlu_end'] = time.time()

    timings['reason_start'] = time.time()
    session_memory = SessionMemory()
    response_text, trace = handle_appointment(intent, slots, session_memory)
    timings['reason_end'] = time.time()

    timings['tts_start'] = time.time()
    audio_out = tts_speak(response_text, lang)
    timings['tts_end'] = time.time()

    timings['total'] = timings['tts_end'] - timings['stt_start']
    return audio_out, trace, timings