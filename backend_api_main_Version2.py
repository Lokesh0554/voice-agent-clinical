from fastapi import FastAPI, UploadFile, File, Request
from orchestrator.agent import process_audio_pipeline

app = FastAPI()

@app.post('/api/v1/voice')
async def voice_endpoint(file: UploadFile = File(...)):
    audio = await file.read()
    try:
        result_audio, agent_trace, timings = process_audio_pipeline(audio)
        # For demo: send reasoning trace and timings, not audio file.
        return {"trace": agent_trace, "timings": timings}
    except Exception as e:
        return {"error": str(e)}