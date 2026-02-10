from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI CONFIGURATION ---
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
        
        # PROMPT UPDATED: For 5-6 lines summary and detailed sections
        prompt = f"""
        You are a Senior Resume Writer. Create highly detailed resume content for:
        Name: {data.name}
        Target Role: {data.title}
        Core Skills: {data.skills}

        Instructions for a Realistic Resume:
        1. PROFESSIONAL SUMMARY: Write a long, sophisticated summary (minimum 5-6 lines). Focus on career goals, technical passion, and how the user solves problems using {data.skills}.
        2. EXPERIENCE/ROLES: Provide 4 detailed points. Each point should be 2-3 lines long, explaining a specific task and its positive result (e.g., "Used {data.skills} to optimize performance by 30%...").
        3. EDUCATION/LEVEL CONTEXT: Add a small 2-line commentary based on the user's career stage (Fresher or Experienced).

        Return ONLY a JSON object:
        {{
            "summary": "Detailed 6-line summary text...",
            "responsibilities": [
                "Detailed 3-line point about technical execution...",
                "Detailed 3-line point about team collaboration...",
                "Detailed 3-line point about problem solving...",
                "Detailed 3-line point about learning and growth..."
            ],
            "education_note": "A realistic line about academic background and skill application."
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
        # Realistic Fallback in case of error
        return {
            "status": "success",
            "ai_content": {
                "summary": f"Results-driven professional with a deep interest in {data.title}. Possessing a strong foundation in {data.skills}, I am committed to delivering high-quality solutions and continuous learning. My approach combines technical expertise with a problem-solving mindset to drive innovation and efficiency. I aim to contribute effectively to team goals while staying updated with the latest industry trends and best practices to ensure top-notch project delivery.",
                "responsibilities": [
                    f"Actively developed and maintained core features using {data.skills} to ensure seamless user experience and system reliability across all platforms.",
                    "Collaborated with cross-functional teams to identify bottlenecks and implement optimized workflows, resulting in improved project delivery timelines.",
                    "Leveraged analytical skills to debug complex issues and provide robust fixes, maintaining a high standard of code quality and performance.",
                    "Participated in continuous training and knowledge sharing sessions to stay ahead of emerging technologies and integrate them into current projects."
                ],
                "education_note": "Focused academic background with a specialization in technologies that align with current industry demands."
            }
        }

if __name__ == "__main__":
    import uvicorn
    import os
    # Port ko environment variable se uthayega, warna default 8000 lega
    port = int(os.environ.get("PORT", 8000))
    # Host 0.0.0.0 ka matlab hai ki ye internet par accessible hoga
    uvicorn.run(app, host="0.0.0.0", port=port)
