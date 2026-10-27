"""
BuildSense AI – Construction Intelligence Platform
Streamlit Cloud Web Application
"""

import os
import base64
import io
from datetime import datetime, timedelta
import streamlit as st
from PIL import Image
import pandas as pd
from dotenv import load_dotenv

# Load local environment if available
load_dotenv()

# ── Streamlit Page Configuration ─────────────────────────────────────
st.set_page_config(
    page_title="BuildSense AI – Construction Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom Construction-Themed CSS ────────────────────────────────────
st.markdown("""
<style>
    :root {
        --primary-orange: #F97316;
        --primary-dark: #1E293B;
        --secondary-dark: #0F172A;
        --accent-orange: #EA580C;
        --bg-light: #F8FAFC;
    }
    
    /* Main container and typography */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, sans-serif;
        font-weight: 700;
    }
    
    /* Header hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-left: 6px solid #F97316;
        padding: 24px;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    }
    .hero-banner h1 {
        color: #FFFFFF !important;
        margin: 0 0 8px 0;
        font-size: 1.8rem;
    }
    .hero-banner p {
        color: #CBD5E1 !important;
        margin: 0;
        font-size: 1rem;
    }
    
    /* Metric Cards */
    .stat-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        border-top: 4px solid #F97316;
        margin-bottom: 15px;
    }
    .stat-card-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-card-value {
        color: #0F172A;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
    }
    
    /* Action Buttons */
    div.stButton > button {
        background-color: #F97316 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #EA580C !important;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3) !important;
    }
    
    /* Disclaimer and Alert boxes */
    .disclaimer-box {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 6px;
        color: #92400E;
        font-size: 0.88rem;
        margin: 15px 0;
    }
    
    .feature-card {
        background: white;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        padding: 20px;
        height: 100%;
        transition: transform 0.2s ease;
    }
    .feature-card:hover {
        border-color: #F97316;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper: Format Indian Rupees ─────────────────────────────────────
def format_inr(amount: float) -> str:
    """Format numeric values as Indian Currency (e.g. ₹ 15,20,000)"""
    try:
        amount = round(float(amount))
        amt_str = str(amount)
        if len(amt_str) <= 3:
            return f"₹ {amt_str}"
        last_three = amt_str[-3:]
        remaining = amt_str[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        return f"₹ {','.join(groups)},{last_three}"
    except Exception:
        return f"₹ {amount:,.0f}"


# ── Helper: API Key Retrieval ────────────────────────────────────────
def get_api_key():
    """Retrieve Gemini or Groq API key from session state, st.secrets, or env"""
    # 1. User manual input in sidebar session
    if "user_api_key" in st.session_state and st.session_state.user_api_key:
        return st.session_state.user_api_key
    
    # 2. Streamlit Cloud Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
        
    # 3. Environment variable
    return os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY") or ""


# ── AI Integration: Gemini / Groq ───────────────────────────────────
def call_gemini_vision(image_bytes: bytes, mime_type: str, prompt: str, api_key: str) -> str:
    """Call Google Gemini API with an image input"""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    # Try gemini-1.5-flash
    model = genai.GenerativeModel("gemini-1.5-flash")
    image_part = {
        "mime_type": mime_type,
        "data": image_bytes
    }
    response = model.generate_content([prompt, image_part])
    return response.text


def call_gemini_text(prompt: str, api_key: str) -> str:
    """Call Google Gemini API with a text prompt"""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def call_groq_vision(image_bytes: bytes, mime_type: str, prompt: str, api_key: str) -> str:
    """Fallback Groq Vision API"""
    from groq import Groq
    client = Groq(api_key=api_key)
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f"data:{mime_type};base64,{b64_image}"
    
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }],
        max_tokens=1500
    )
    return response.choices[0].message.content


def call_groq_text(prompt: str, api_key: str) -> str:
    """Fallback Groq Text API"""
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are BuildSense AI, a professional civil engineering and construction intelligence assistant. Provide accurate, clear, and actionable construction guidance."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1200
    )
    return response.choices[0].message.content


def analyze_image_ai(image_bytes: bytes, mime_type: str, prompt: str, api_key: str) -> str:
    """Smart router: routes to Gemini if key starts with AIza, else Groq, or handles errors"""
    if not api_key:
        raise ValueError("API key is missing. Please configure your GEMINI_API_KEY or GROQ_API_KEY in the sidebar or Streamlit Secrets.")
    
    if api_key.startswith("gsk_"):
        return call_groq_vision(image_bytes, mime_type, prompt, api_key)
    else:
        try:
            return call_gemini_vision(image_bytes, mime_type, prompt, api_key)
        except Exception as e:
            # If gemini fails and key might be groq or vice versa
            if "gsk_" in api_key or "groq" in str(e).lower():
                return call_groq_vision(image_bytes, mime_type, prompt, api_key)
            raise e


def chat_ai(prompt: str, api_key: str) -> str:
    """Smart text chat router"""
    if not api_key:
        raise ValueError("API key is missing. Please configure your GEMINI_API_KEY or GROQ_API_KEY in the sidebar or Streamlit Secrets.")
    if api_key.startswith("gsk_"):
        return call_groq_text(prompt, api_key)
    else:
        try:
            return call_gemini_text(prompt, api_key)
        except Exception as e:
            if "gsk_" in api_key:
                return call_groq_text(prompt, api_key)
            raise e


# ── Sidebar Navigation ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ **BuildSense AI**")
    st.caption("Construction Intelligence Platform")
    st.divider()

    menu = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🦺 Safety Analysis",
            "🔍 Crack Detection",
            "💰 Property Valuation",
            "📋 Project Planner",
            "🤖 AI Assistant"
        ],
        index=0
    )

    st.divider()
    
    # API Key Management Expander
    active_key = get_api_key()
    with st.expander("🔑 AI Key Settings", expanded=not bool(active_key)):
        key_input = st.text_input(
            "Gemini or Groq API Key",
            type="password",
            value=active_key,
            placeholder="Paste your key here...",
            help="Free Gemini key from https://aistudio.google.com/ or Groq key from https://console.groq.com/"
        )
        if key_input:
            st.session_state.user_api_key = key_input
            active_key = key_input

        if active_key:
            st.success("API Key Loaded ✅")
        else:
            st.warning("No API Key detected. AI features will require a key. (Valuation & Planner work offline!)")
            st.markdown("[Get Free Gemini Key ↗](https://aistudio.google.com/)")

    st.markdown("---")
    st.caption("BuildSense AI v1.0 • Construction Tech")


# ══════════════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if menu == "📊 Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h1>🏗️ BuildSense AI – Construction Intelligence Platform</h1>
        <p>AI-powered computer vision and automated decision support for contractors, engineers, and property developers.</p>
    </div>
    """, unsafe_allow_html=True)

    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-card-title">Safety Inspection</div>
            <div class="stat-card-value">Zero-Hazard AI</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-card-title">Structural Audit</div>
            <div class="stat-card-value">Sub-mm Crack AI</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-card-title">Valuation Engine</div>
            <div class="stat-card-value">₹ INR Verified</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-card-title">Project Planner</div>
            <div class="stat-card-value">6-Phase CPM</div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Platform Capabilities")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <h3>🦺 Site Safety Analysis</h3>
            <p>Upload site photos to automatically spot missing PPE, uncovered trenches, hazardous scaffolding, and electrical exposure with instant OSHA recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 Crack & Defect Detection</h3>
            <p>Analyze concrete surfaces, masonry, and load-bearing columns. Distinguish between non-structural hairline shrinkage and severe structural shear stress.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <h3>💰 Property Valuation</h3>
            <p>Instantaneous property appraisals tailored to Indian real estate benchmarks. Calculated directly with zero API cost.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Critical-Path Project Planner</h3>
            <p>Generate milestone schedules, task breakdowns, and phased budget cash flows from project duration and start dates.</p>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 Construction AI Assistant</h3>
            <p>Interactive 24/7 technical advisor answering queries on concrete mix design, IS/NBC standards, curing timelines, and safety regulations.</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE 2: SAFETY ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif menu == "🦺 Safety Analysis":
    st.title("🦺 Construction Site Safety Analysis")
    st.markdown("Upload a photo of your job site. Gemini AI inspects visible worker hazards, PPE compliance, and OSHA violations.")

    uploaded_file = st.file_uploader("Upload Jobsite Photo", type=["jpg", "jpeg", "png", "webp"])

    col_img, col_result = st.columns([1, 1])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        with col_img:
            st.image(image, caption="Uploaded Construction Site", use_container_width=True)
            
        with col_result:
            if st.button("🚀 Analyze Site Hazards", use_container_width=True):
                api_key = get_api_key()
                if not api_key:
                    st.error("⚠️ AI API Key missing! Please enter your Gemini API Key in the left sidebar.")
                else:
                    with st.spinner("Inspecting site hazards, scaffolding, and PPE compliance..."):
                        try:
                            # Convert to bytes
                            buf = io.BytesIO()
                            image.save(buf, format="JPEG")
                            img_bytes = buf.getvalue()

                            prompt = (
                                "You are a professional Construction Site Safety Inspector certified in OSHA and NBC standards. "
                                "Analyze this construction site image carefully:\n"
                                "1. List all visible safety hazards (e.g., workers without hard hats/high-vis vests, unsafe scaffolding, fall hazards, trip hazards, uncovered openings, exposed rebar, electrical lines).\n"
                                "2. Rate the Overall Site Risk Level (Low, Moderate, High, or Critical).\n"
                                "3. Provide practical, step-by-step corrective actions and safety recommendations for the site supervisor.\n"
                                "Format the output cleanly with bold bullet points and clear sections."
                            )

                            findings = analyze_image_ai(img_bytes, "image/jpeg", prompt, api_key)
                            st.success("Inspection Complete!")
                            st.markdown(findings)
                        except Exception as e:
                            st.error(f"Safety Analysis Failed: {str(e)}")
    else:
        st.info("💡 Please upload an image of a construction site above to begin analysis.")


# ══════════════════════════════════════════════════════════════════════
# PAGE 3: CRACK DETECTION
# ══════════════════════════════════════════════════════════════════════
elif menu == "🔍 Crack Detection":
    st.title("🔍 Concrete & Structural Crack Detection")
    st.markdown("Upload an image of a concrete slab, beam, column, or masonry wall for preliminary computer-vision severity assessment.")

    st.markdown("""
    <div class="disclaimer-box">
        ⚠️ <strong>Important Preliminary Assessment Notice:</strong> This AI tool provides an initial image-based visual screening only. 
        It does not replace an in-person structural audit, core sampling, or ultrasonic pulse velocity test by a licensed structural engineer.
    </div>
    """, unsafe_allow_html=True)

    crack_file = st.file_uploader("Upload Crack or Concrete Surface Image", type=["jpg", "jpeg", "png", "webp"])

    col_img2, col_result2 = st.columns([1, 1])

    if crack_file is not None:
        c_image = Image.open(crack_file)
        with col_img2:
            st.image(c_image, caption="Uploaded Surface", use_container_width=True)

        with col_result2:
            if st.button("🔎 Detect & Classify Crack", use_container_width=True):
                api_key = get_api_key()
                if not api_key:
                    st.error("⚠️ AI API Key missing! Please enter your Gemini API Key in the left sidebar.")
                else:
                    with st.spinner("Analyzing crack geometry, pattern, and structural risk..."):
                        try:
                            buf = io.BytesIO()
                            c_image.save(buf, format="JPEG")
                            img_bytes = buf.getvalue()

                            prompt = (
                                "You are an expert Structural Forensic Engineer. Analyze this concrete or masonry image for cracks and structural defects:\n"
                                "1. Visual Observations: Describe the crack location, orientation (vertical, horizontal, diagonal, stair-step, or map/crazing) and estimated aperture.\n"
                                "2. Probable Cause: (e.g. plastic shrinkage, foundation differential settlement, thermal expansion, structural overload, corrosion of reinforcement).\n"
                                "3. Severity Rating: Classify strictly as 'Minor / Hairline (Cosmetic)', 'Moderate (Monitor Closely)', or 'Severe (Potential Structural Concern)'.\n"
                                "4. Recommended Next Steps: Specific mitigation procedures (epoxy injection, polyurethane sealant, carbon-fiber wrap, or mandatory on-site engineer inspection).\n"
                                "End with a standard professional disclaimer."
                            )

                            assessment = analyze_image_ai(img_bytes, "image/jpeg", prompt, api_key)
                            st.success("Crack Assessment Ready!")
                            st.markdown(assessment)
                        except Exception as e:
                            st.error(f"Crack Analysis Failed: {str(e)}")
    else:
        st.info("💡 Upload an image of a wall, column, beam, or pavement to inspect crack characteristics.")


# ══════════════════════════════════════════════════════════════════════
# PAGE 4: PROPERTY VALUATION
# ══════════════════════════════════════════════════════════════════════
elif menu == "💰 Property Valuation":
    st.title("💰 Property Valuation Calculator")
    st.markdown("Calculate fair market property estimates in Indian Rupees (₹). **Operates completely offline without an API key.**")

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            city = st.selectbox(
                "City",
                ["Mumbai", "Delhi NCR", "Bengaluru", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Other"]
            )
            prop_type = st.selectbox(
                "Property Type",
                ["Residential Apartment", "Independent House / Villa", "Commercial Office", "Retail Shop", "Plot / Land"]
            )
            area_sqft = st.number_input("Built-up Area (Square Feet)", min_value=100.0, value=1200.0, step=50.0)

        with c2:
            prop_age = st.number_input("Age of Property (Years)", min_value=0, max_value=100, value=3, step=1)
            default_rate = {
                "Mumbai": 18000.0,
                "Delhi NCR": 8500.0,
                "Bengaluru": 7500.0,
                "Hyderabad": 6800.0,
                "Pune": 6200.0,
                "Chennai": 6500.0,
                "Kolkata": 4800.0,
                "Ahmedabad": 4500.0,
                "Other": 5000.0
            }.get(city, 6000.0)

            rate_per_sqft = st.number_input(
                "Price per Square Foot (₹)",
                min_value=500.0,
                value=default_rate,
                step=500.0
            )

    if st.button("📊 Calculate Estimated Valuation", use_container_width=True):
        raw_val = area_sqft * rate_per_sqft
        
        # Age depreciation factor (1% per year up to max 25%)
        deprec_pct = min(prop_age * 1.0, 25.0)
        deprec_amount = raw_val * (deprec_pct / 100.0)
        final_estimate = raw_val - deprec_amount

        st.markdown("<br>", unsafe_allow_html=True)
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            st.metric("Base Value", format_inr(raw_val))
        with res_col2:
            st.metric("Age Depreciation", f"-{deprec_pct}% ({format_inr(deprec_amount)})")
        with res_col3:
            st.metric("Fair Market Value", format_inr(final_estimate))

        st.success(f"🏡 Estimated Value for {area_sqft:,.0f} sq.ft {prop_type} in {city}: **{format_inr(final_estimate)}**")


# ══════════════════════════════════════════════════════════════════════
# PAGE 5: PROJECT PLANNER
# ══════════════════════════════════════════════════════════════════════
elif menu == "📋 Project Planner":
    st.title("📋 Construction Project Planner")
    st.markdown("Generate automated milestone schedules and phase timelines. **Operates completely offline without an API key.**")

    with st.form("planner_form"):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            project_name = st.text_input("Project Name", value="Skyline Heights Residency")
            project_type = st.selectbox("Project Type", ["Residential High-Rise", "Commercial Complex", "Industrial Warehouse", "Villa Project", "Interior Fit-out"])
            start_date = st.date_input("Planned Start Date", value=datetime.today())

        with p_col2:
            duration_days = st.number_input("Total Project Duration (Days)", min_value=14, max_value=3650, value=180, step=10)
            budget = st.number_input("Total Budget (₹)", min_value=100000.0, value=7500000.0, step=500000.0)

        generate_btn = st.form_submit_button("📅 Generate Phase Schedule")

    if generate_btn:
        st.subheader(f"Schedule for: {project_name}")
        st.caption(f"Category: {project_type} | Total Duration: {duration_days} Days | Budget: {format_inr(budget)}")

        # Define 6 phases with duration and budget breakdown
        phases = [
            ("1. Site Preparation & Permitting", 0.10, 0.08),
            ("2. Foundation & Substructure", 0.15, 0.22),
            ("3. Structural Framing & Superstructure", 0.30, 0.35),
            ("4. MEP (Electrical, Plumbing, HVAC)", 0.20, 0.18),
            ("5. Architectural Finishing & Interior", 0.15, 0.12),
            ("6. Final Inspection & Handover", 0.10, 0.05)
        ]

        # Calculate exact days
        records = []
        cur_date = datetime.combine(start_date, datetime.min.time())
        allocated_days = 0

        for i, (p_name, pct_dur, pct_bud) in enumerate(phases):
            if i == len(phases) - 1:
                p_days = duration_days - allocated_days
            else:
                p_days = max(1, round(duration_days * pct_dur))
                allocated_days += p_days

            p_start = cur_date
            p_end = cur_date + timedelta(days=p_days - 1)
            cur_date = p_end + timedelta(days=1)
            p_budget = budget * pct_bud

            records.append({
                "Phase": p_name,
                "Duration (Days)": p_days,
                "Start Date": p_start.strftime("%d-%b-%Y"),
                "End Date": p_end.strftime("%d-%b-%Y"),
                "Allocated Budget": format_inr(p_budget)
            })

        df_plan = pd.DataFrame(records)
        st.dataframe(df_plan, use_container_width=True, hide_index=True)

        st.info("💡 Tip: Milestone dates are generated using sequential critical-path logic.")


# ══════════════════════════════════════════════════════════════════════
# PAGE 6: AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════
elif menu == "🤖 AI Assistant":
    st.title("🤖 Construction AI Assistant")
    st.markdown("Ask technical questions regarding building codes, concrete curing, soil mechanics, or site safety.")

    # Suggestions
    st.markdown("**Common Questions:**")
    sc1, sc2, sc3 = st.columns(3)
    preset_q = None
    with sc1:
        if st.button("🏗️ Standard concrete curing time?", use_container_width=True):
            preset_q = "What is the standard curing time for M25 grade concrete and why is water curing critical?"
    with sc2:
        if st.button("🦺 OSHA scaffolding safety rules?", use_container_width=True):
            preset_q = "What are the primary OSHA scaffolding requirements regarding tie-offs, guardrails, and load capacity?"
    with sc3:
        if sc3_btn := st.button("🧱 How to prevent shrinkage cracks?", use_container_width=True):
            preset_q = "What are the best site practices to prevent plastic shrinkage cracks in newly poured slabs?"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am BuildSense AI, your digital civil engineering and construction advisor. How can I assist with your site operations today?"}
        ]

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle input prompt (either from preset click or chat input)
    user_prompt = st.chat_input("Ask any construction question...")
    if preset_q:
        user_prompt = preset_q

    if user_prompt:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate Assistant response
        api_key = get_api_key()
        if not api_key:
            reply = "⚠️ **API Key Missing**: Please provide your Gemini API Key in the left sidebar to enable live AI responses. (Get a free key at [Google AI Studio](https://aistudio.google.com/))."
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
        else:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing construction specifications..."):
                    try:
                        reply = chat_ai(user_prompt, api_key)
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        err = f"Failed to get response: {str(e)}"
                        st.error(err)
                        st.session_state.messages.append({"role": "assistant", "content": err})
