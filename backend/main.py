"""
BuildSense AI - Construction Intelligence Platform
FastAPI Backend Server

This is the main backend file that handles all API endpoints for:
- Safety Analysis (AI-powered)
- Crack Detection (AI-powered)
- Property Valuation (calculation-based)
- Project Planning (calculation-based)
- AI Assistant Chat (AI-powered)
"""

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import google.generativeai as genai

# ── Load environment variables ──────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── Gemini model name (change this to switch models easily) ─────────
GEMINI_MODEL = "gemini-1.5-flash"

# ── Configure Gemini SDK ────────────────────────────────────────────
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ── Create FastAPI app ──────────────────────────────────────────────
app = FastAPI(
    title="BuildSense AI",
    description="Construction Intelligence Platform API",
    version="1.0.0",
)

# ── CORS (allow frontend to call backend during development) ────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════

def check_api_key():
    """Raise an error if the Gemini API key is not configured."""
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="Gemini API key is not configured. Please add GEMINI_API_KEY to your .env file.",
        )


def format_indian_currency(amount: float) -> str:
    """
    Format a number in the Indian numbering system.
    Example: 1234567 → ₹12,34,567
    """
    amount = round(amount)
    amount_str = str(amount)

    if len(amount_str) <= 3:
        return f"₹{amount_str}"

    # Last 3 digits
    last_three = amount_str[-3:]
    # Remaining digits, grouped in pairs
    remaining = amount_str[:-3]

    # Add commas every 2 digits from the right in the remaining part
    groups = []
    while len(remaining) > 2:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        groups.insert(0, remaining)

    formatted_remaining = ",".join(groups)
    return f"₹{formatted_remaining},{last_three}"


# ═══════════════════════════════════════════════════════════════════
# Pydantic Models (for request validation)
# ═══════════════════════════════════════════════════════════════════

class ValuationRequest(BaseModel):
    city: str
    property_type: str
    area_sqft: float = Field(gt=0, description="Area in square feet")
    age_years: float = Field(ge=0, description="Age of property in years")
    price_per_sqft: float = Field(gt=0, description="Price per square foot in INR")


class PlanningRequest(BaseModel):
    project_name: str
    project_type: str
    start_date: str
    duration_days: int = Field(gt=0, description="Total project duration in days")
    budget: float = Field(gt=0, description="Project budget in INR")


class ChatRequest(BaseModel):
    message: str


# ═══════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health_check():
    """Check if the server is running and if Gemini is configured."""
    return {
        "status": "ok",
        "gemini_configured": GEMINI_API_KEY is not None and len(GEMINI_API_KEY) > 0,
    }


# ── Safety Analysis ─────────────────────────────────────────────────

@app.post("/api/safety/analyze")
async def analyze_safety(file: UploadFile = File(...)):
    """Analyze a construction site image for safety hazards using Gemini AI."""
    check_api_key()

    try:
        # Read the uploaded image
        image_bytes = await file.read()

        # Create the image part for Gemini
        image_part = {
            "mime_type": file.content_type,
            "data": image_bytes,
        }

        # Prompt for safety analysis
        prompt = (
            "You are a construction safety expert. "
            "Analyze this construction site image and identify:\n"
            "1. Visible safety hazards\n"
            "2. PPE compliance issues\n"
            "3. Environmental risks\n"
            "4. Safety recommendations\n\n"
            "Provide a clear, structured response with findings and recommendations."
        )

        # Send to Gemini
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content([prompt, image_part])

        return {"analysis": response.text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


# ── Crack Detection ─────────────────────────────────────────────────

@app.post("/api/cracks/analyze")
async def analyze_cracks(file: UploadFile = File(...)):
    """Analyze an image for structural cracks using Gemini AI."""
    check_api_key()

    try:
        # Read the uploaded image
        image_bytes = await file.read()

        # Create the image part for Gemini
        image_part = {
            "mime_type": file.content_type,
            "data": image_bytes,
        }

        # Prompt for crack detection
        prompt = (
            "You are a structural engineering expert. "
            "Analyze this image for cracks and structural damage:\n"
            "1. Describe any visible cracks (location, pattern, width estimate)\n"
            "2. Assess potential severity (cosmetic, moderate, severe)\n"
            "3. Identify possible causes\n"
            "4. Recommend next steps\n\n"
            "Note: This is a preliminary image-based assessment only. "
            "A professional on-site inspection is required for definitive analysis."
        )

        # Send to Gemini
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content([prompt, image_part])

        return {"analysis": response.text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


# ── Property Valuation (No API key needed) ──────────────────────────

@app.post("/api/valuation/estimate")
def estimate_valuation(data: ValuationRequest):
    """Calculate a simple property valuation estimate."""
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


# ── Project Planning (No API key needed) ────────────────────────────

@app.post("/api/planning/generate")
def generate_plan(data: PlanningRequest):
    """Generate a basic construction project schedule."""

    # Parse the start date
    try:
        start = datetime.strptime(data.start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Define phases with their percentage of total duration
    phases = [
        ("Site Preparation", 0.10),
        ("Foundation", 0.15),
        ("Structural Work", 0.30),
        ("Electrical & Plumbing", 0.20),
        ("Finishing", 0.15),
        ("Final Inspection", 0.10),
    ]

    # Calculate duration for each phase (minimum 1 day each)
    phase_durations = []
    for name, percentage in phases:
        days = max(1, round(data.duration_days * percentage))
        phase_durations.append((name, days))

    # Adjust the last phase so total matches exactly
    total_allocated = sum(d for _, d in phase_durations)
    diff = data.duration_days - total_allocated
    last_name, last_days = phase_durations[-1]
    phase_durations[-1] = (last_name, max(1, last_days + diff))

    # Build the schedule with dates
    schedule = []
    current_date = start

    for phase_name, duration in phase_durations:
        phase_start = current_date
        phase_end = current_date + timedelta(days=duration - 1)  # Inclusive end date

        schedule.append({
            "phase": phase_name,
            "duration_days": duration,
            "start_date": phase_start.strftime("%Y-%m-%d"),
            "end_date": phase_end.strftime("%Y-%m-%d"),
        })

        current_date = phase_end + timedelta(days=1)  # Next phase starts the day after

    return {
        "project_name": data.project_name,
        "project_type": data.project_type,
        "total_duration": data.duration_days,
        "budget": data.budget,
        "formatted_budget": format_indian_currency(data.budget),
        "schedule": schedule,
    }


# ── AI Assistant Chat ───────────────────────────────────────────────

@app.post("/api/assistant/chat")
def chat_with_assistant(data: ChatRequest):
    """Answer construction-related questions using Gemini AI."""
    check_api_key()

    try:
        prompt = (
            "You are BuildSense AI, a helpful construction industry assistant. "
            "Answer the following construction-related question clearly and concisely:\n\n"
            f"{data.message}"
        )

        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        return {"response": response.text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response: {str(e)}")


# ── Run with: uvicorn main:app --reload ─────────────────────────────
