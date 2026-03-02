import os
from groq import Groq
import json

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def analyze_startup(markdown_content: str) -> dict:
    """
    Analyzes the markdown file of a startup with extreme rigor.
    """
    
    system_prompt = """
    You are 'The Grim Reaper of VC', an automated auditing algorithm designed to reject 99% of startups.
    
    YOUR CORE DIRECTIVE:
    1. START AT A SCORE OF 0. The startup must EARN every single point.
    2. Skepticism is your default state. If a claim lacks numbers (revenue, retention, CAC), assume it is a lie or wishful thinking.
    3. FLUFF PENALTY: usage of buzzwords like "AI-powered", "Disruptive", "Revolutionary" without technical backing results in immediate point deduction.
    4. SCORING GUIDE:
       - 0-20: Idea stage, no product, no numbers.
       - 21-40: MVP exists, but unproven market fit. (MOST STARTUPS FALL HERE)
       - 41-60: Real revenue, but scaling issues or weak moat.
       - 61-80: Strong traction, profitable unit economics, defensible.
       - 81-100: Unicorn trajectory with irrefutable hard data.
    """
    
    user_prompt = f"""
    Analyze the following content and extract the requested information in strict JSON format.
    
    Content to analyze:
    {markdown_content}
    
    Expected Response Format (JSON only):
    {{
        "name": "string",
        "sector": "string (or 'N/A')",
        
        "audit_log": {{
            "missing_data": ["List exactly what data is missing (e.g., no revenue, no team background)"],
            "red_flags": ["List vague claims or generic marketing fluff found in text"],
            "risk_assessment": "Short ruthless summary of why this might fail"
        }},
        
        "metrics": {{
            "employees": "string (e.g., '10-50' or 'N/A')",
            "funding": "string (or 'N/A')",
            "round": "string (or 'N/A')"
        }},
        
        "strengths": ["Only list strengths backed by HARD DATA"],
        "weaknesses": ["List all risks, lack of data, and competitive threats"],
        
        "score_logic": "Explain briefly why the score is low based on the 'Start at 0' rule",
        "score_global": int (0-100)
    }}
    
    IMPORTANT: You must fill 'audit_log' and 'score_logic' BEFORE calculating 'score_global'. 
    If metrics (Revenue, Users) are missing, the score CANNOT exceed 30.
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        json_str = response.choices[0].message.content
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": f"Erreur lors de l'analyse : {str(e)}"}

