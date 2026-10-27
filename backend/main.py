
import os
import base64
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "qwen/qwen3.8-27b"

app = FastAPI(
    title="BuildSense AI",
    description="Construction Intelligence Platform API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_groq_client():
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Groq API key is missing. Add GROQ_API_KEY to backend/.env and restart the backend.",
        )
    return Groq(api_key=GROQ_API_KEY)


def format_indian_currency(amount: float) -> str:
    amount_str = str(round(amount))
    if len(amount_str) <= 3:
        return f"₹{amount_str}"
    last_three = amount_str[-3:]
    remaining = amount_str[:-3]
    groups = []
    while len(remaining) > 2:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        groups.insert(0, remaining)
    return f"₹{','.join(groups)},{last_three}"


def analyze_image_with_groq(file_bytes: bytes, mime_type: str, prompt: str) -> str:
    client = get_groq_client()
    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{encoded_image}"

    result = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ],
            }
        ],
        max_completion_tokens=1200,
    )
    return result.choices[0].message.content or "No analysis was returned."


class ValuationRequest(BaseModel):
    city: str
    property_type: str
    area_sqft: float = Field(gt=0)
    age_years: float = Field(ge=0)
    price_per_sqft: float = Field(gt=0)


class PlanningRequest(BaseModel):
    project_name: str
    project_type: str
    start_date: str
    duration_days: int = Field(gt=0)
    budget: float = Field(gt=0)


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "groq_configured": bool(GROQ_API_KEY),
    }


@app.post("/api/safety/analyze")
async def analyze_safety(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(status_code=400, detail="Upload a JPEG, PNG, WEBP, or GIF image.")

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The uploaded image is empty.")

        prompt = (
            "You are a construction safety assistant. Analyze this image for "
            "visible safety hazards, PPE compliance, environmental risks, and "
            "practical safety recommendations. Clearly state that image-based "
            "analysis may miss hazards and does not replace a site inspection."
        )
        return {
            "analysis": analyze_image_with_groq(
                image_bytes, file.content_type, prompt
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety analysis failed: {e}")


@app.post("/api/cracks/analyze")
async def analyze_cracks(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(status_code=400, detail="Upload a JPEG, PNG, WEBP, or GIF image.")

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The uploaded image is empty.")

        prompt = (
            "You are an assistant for preliminary visual assessment of buildings. "
            "Describe visible cracks, their location and pattern, possible causes, "
            "and potential concerns. Do not claim to measure crack width precisely "
            "from an image. Recommend professional inspection when appropriate. "
            "This is not a structural safety certification."
        )
        return {
            "analysis": analyze_image_with_groq(
                image_bytes, file.content_type, prompt
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crack analysis failed: {e}")


@app.post("/api/valuation/estimate")
def estimate_valuation(data: ValuationRequest):
    estimated_value = data.area_sqft * data.price_per_sqft
    return {
        "estimated_value": estimated_value,
        "formatted_value": format_indian_currency(estimated_value),
        "inputs": {
            "city": data.city,
            "property_type": data.property_type,
            "area_sqft": data.area_sqft,
            "age_years": data.age_years,
            "price_per_sqft": data.price_per_sqft,
        },
    }


@app.post("/api/planning/generate")
def generate_plan(data: PlanningRequest):
    try:
        start = datetime.strptime(data.start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD.",
        )

    phases = [
        ("Site Preparation", 0.10),
        ("Foundation", 0.15),
        ("Structural Work", 0.30),
        ("Electrical & Plumbing", 0.20),
        ("Finishing", 0.15),
        ("Final Inspection", 0.10),
    ]

    phase_durations = [
        (name, max(1, round(data.duration_days * pct)))
        for name, pct in phases
    ]

    # Ensure the planned phase durations add up to the requested duration.
    durations = [days for _, days in phase_durations]
    if data.duration_days >= len(phases):
        for i in range(len(durations)):
            durations[i] = 1
        remaining = data.duration_days - len(phases)
        for i, (_, pct) in enumerate(phases):
            extra = round(remaining * pct)
            durations[i] += extra
        durations[-1] += data.duration_days - sum(durations)

    schedule = []
    current_date = start
    for (name, _), duration in zip(phases, durations):
        end_date = current_date + timedelta(days=duration - 1)
        schedule.append({
            "phase": name,
            "duration_days": duration,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        })
        current_date = end_date + timedelta(days=1)

    return {
        "project_name": data.project_name,
        "project_type": data.project_type,
        "total_duration": data.duration_days,
        "budget": data.budget,
        "formatted_budget": format_indian_currency(data.budget),
        "schedule": schedule,
    }


@app.post("/api/assistant/chat")
def chat_with_assistant(data: ChatRequest):
    try:
        client = get_groq_client()
        result = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are BuildSense AI, a helpful construction industry "
                        "assistant. Give clear, practical answers. For safety-critical "
                        "or structural questions, recommend qualified professionals."
                    ),
                },
                {"role": "user", "content": data.message},
            ],
            max_completion_tokens=1200,
        )
        return {
            "response": result.choices[0].message.content
            or "No response was returned."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant request failed: {e}")
