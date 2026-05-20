def log_latency(timings):
    print("--- Latency Breakdown ---")
    for step in ['stt', 'nlu', 'reason', 'tts']:
        start = timings.get(f"{step}_start")
        end = timings.get(f"{step}_end")
        if start and end:
            print(f"{step.upper()}: {end - start:.2f}s")
    print(f"TOTAL: {timings['total']:.2f}s")