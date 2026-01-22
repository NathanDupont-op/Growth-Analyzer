import ollama
import json

def analyze_startup(markdown_content: str) -> dict:
    """
    Analyse le contenu markdown d'une startup en utilisant un modèle local Ollama.
    Retourne un dictionnaire structuré avec les scores et l'analyse.
    """
    system_prompt = "You are an expert VC analyst. Extract structured information from the text and rate the startup out of 100 based on factor linked to potential growth"
    
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
        response = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ], format='json')
        
        # Le contenu de la réponse est une chaîne JSON
        json_str = response['message']['content']
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": f"Erreur lors de l'analyse : {str(e)}"}
