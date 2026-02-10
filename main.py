from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
import os

app = FastAPI()

# --- 1. CORS SETTINGS (Netlify connection ke liye zaroori) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. AI CONFIGURATION ---
# Note: LinkedIn par share karne se pehle API Key ko "Environment Variable" mein daalna safe hota hai
GEMINI_API_KEY = "AIzaSyBUbvuovM01d_XqNOo3PJEyrHvd81KS6hI"
genai.configure(api_key=GEMINI_API_KEY)

class ResumeData(BaseModel):
    name: str
    title: str
    skills: str
    email: str = ""
    phone: str = ""
    city: str = ""
    state: str = ""
    education: list = []

@app.post("/api/generate-resume")
async def process_resume(data: ResumeData):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a Senior Resume Writer. Create highly detailed resume content for:
        Name: {data.name}
        Target Role: {data.title}
        Core Skills: {data.skills}

        Instructions for a Realistic Resume:
        1. PROFESSIONAL SUMMARY: Write a long, sophisticated summary (minimum 5-6 lines). Focus on career goals, technical passion, and how the user solves problems using {data.skills}.
        2. EXPERIENCE/ROLES: Provide 4 detailed points. Each point should be 2-3 lines long, explaining a specific task and its positive result.
        3. EDUCATION/LEVEL CONTEXT: Add a small 2-line commentary based on the user's career stage.

        Return ONLY a JSON object:
        {{
            "summary": "...",
            "responsibilities": ["...", "...", "...", "..."],
            "education_note": "..."
        }}
        """
        
        response = model.generate_content(prompt)
        res_text = response.text.strip()
        
        if "```json" in res_text:
            res_text = res_text.split("```json")[1].split("```")[0]
        elif "```" in res_text:
            res_text = res_text.split("```")[1].split("```")[0]
        
        ai_json = json.loads(res_text.strip())
        return {"status": "success", "ai_content": ai_json}

    except Exception as e:
        print(f"Error: {str(e)}")
        # Fallback Content
        return {
            "status": "success",
            "ai_content": {
                "summary": f"Results-driven professional with a deep interest in {data.title}. Possessing a strong foundation in {data.skills}...",
                "responsibilities": [
                    f"Actively developed features using {data.skills}...",
                    "Collaborated with cross-functional teams...",
                    "Leveraged analytical skills to debug issues...",
                    "Participated in continuous training..."
                ],
                "education_note": "Focused academic background with specialization in industry-aligned technologies."
            }
        }

# --- 3. RENDER DEPLOYMENT SETTINGS (Ye niche hona chahiye) ---
if __name__ == "__main__":
    import uvicorn
    # Render PORT variable provide karta hai, agar na mile toh 8000 use karega
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
