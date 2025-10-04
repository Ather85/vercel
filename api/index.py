# api/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS for all origins (needed for fetch() to work)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry bundle (assuming it's stored in a JSON file in repo)
with open("telemetry.json") as f:
    telemetry_data = json.load(f)

@app.post("/analytics")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    result = {}

    for region in regions:
        region_data = [r for r in telemetry_data if r["region"] == region]

        if not region_data:
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for l in latencies if l > threshold)

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return result
