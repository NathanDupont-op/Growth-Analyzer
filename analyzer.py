import os
from groq import Groq
import json

# Initialize Groq client
# Ensure GROQ_API_KEY is set in environment variables
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def analyze_startup(markdown_content: str) -> dict:
    """
    Analyse le contenu markdown d'une startup en utilisant l'API Groq (Llama 3).
    Retourne un dictionnaire structuré avec les scores et l'analyse.
    """
    system_prompt = "You are a ruthless VC evaluator. Your goal is to identify weak points and risks. You must grade strictly on a scale of 0-100. Constraint: You are extremely hard to impress. Most startups should score arround 50. Only startups with irrefutable proof of traction and a defensible moat should score above 70. If you find generic statements or lack of hard data, the score must be under 50. Be critical, direct, and justify every point deducted."
    
    # User prompt detailing expected JSON structure
    user_prompt = f"""
    Analyze the following content and extract the requested information in strict JSON format.
    
    Content to analyze:
    {markdown_content}
    
    Expected Response Format (JSON only):
    {{
        "name": "string",
        "sector": "string (e.g., SAAS, fintech, or 'N/A' if unknown)",
        "score_global": int (0-100),
        "metrics": {{
            "employees": "string (e.g., '10-50' or '42' or 'N/A')",
            "funding": "string (e.g., '$12M' or 'Bootstrapped' or 'N/A')",
            "round": "string (e.g., 'Series A' or 'Seed' or 'N/A')"
        }},
        "strengths": ["string", "string", ...],
        "weaknesses": ["string", "string", ...]
    }}
    
    CRITICAL INSTRUCTION: If you cannot find a specific piece of information (employees, funding, round), you MUST set the value to "N/A". DO NOT GUESS or HALLUCINATE data not present in the content. 
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        
        # Le contenu de la réponse est une chaîne JSON
        json_str = response.choices[0].message.content
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": f"Erreur lors de l'analyse : {str(e)}"}




