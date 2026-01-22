from fastapi import FastAPI, HTTPException, Request # Ajout de Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates # Ajout pour le HTML
from pydantic import BaseModel
from scraper import get_startup_content
from analyzer import analyze_startup
from pdf_generator import create_pdf_report
import asyncio
import logging
import time
import sys
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for Windows asyncio loop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Startup Analyzer API")

# Configuration des Templates (Dossier créé à l'étape 1)
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str

def run_cli_scraper(url):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    
    result = subprocess.run(
        [sys.executable, "cli_scraper.py", url],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env
    )
    if result.stderr:
        print(f"DEBUG: Subprocess stderr:\n{result.stderr}")
    if result.returncode != 0:
            return f"Erreur subprocess: {result.stderr}"
    return result.stdout

@app.post("/analyze")
async def analyze_startup_endpoint(request: AnalyzeRequest):
    # ... (Votre code existant reste identique ici) ...
    # Je ne le répète pas pour gagner de la place, gardez votre logique
    print(f"DEBUG: Received request for {request.url}")
    # ... (code inchangé)
    # Copiez-collez votre logique existante ici

@app.post("/download-pdf")
async def download_pdf_endpoint(data: dict):
    # ... (code inchangé) ...
    filename = f"report_{int(time.time())}.pdf"
    create_pdf_report(data, filename)
    return FileResponse(filename, media_type='application/pdf', filename=filename)

# --- C'EST ICI QUE TOUT CHANGE ---
@app.get("/")
async def read_root(request: Request):
    # Au lieu de retourner du JSON, on retourne le fichier HTML
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
