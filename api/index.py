from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json
import os

app = FastAPI()

# ✅ Enable CORS for all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins
    allow_methods=["*"],      # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],      # allow all headers
)

# ✅ Root route for quick testing
@app.get("/")
def root():
    return {"message": "Hello from FastAPI with CORS enabled"}

# ✅ Load telemetry data if file exists
telemetry_data = []
if os.path.exists("telemetry.json"):
    with open("telemetry.json") as f:
        telemetry_data = json.load(f)

@app.post("/analytics")
async def analytics(request: Request):
    if not telemetry_data:
        return {"error": "telemetry.json not found or empty"}

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
