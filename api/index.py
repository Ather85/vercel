from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def telemetry(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold_ms = payload.get("threshold_ms", 0)

    # Load your telemetry data (you’ll mount it or store it in Vercel storage)
    # For now, assume it's bundled as JSON or CSV in your repo
    import json
    import pathlib
    data_path = pathlib.Path(__file__).parent / "telemetry.json"
    with open(data_path) as f:
        telemetry = json.load(f)

    results = {}
    for region in regions:
        region_data = [entry for entry in telemetry if entry["region"] == region]

        latencies = np.array([entry["latency_ms"] for entry in region_data])
        uptimes = np.array([entry["uptime"] for entry in region_data])

        avg_latency = float(latencies.mean())
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(uptimes.mean())
        breaches = int((latencies > threshold_ms).sum())

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches,
        }

    return results
