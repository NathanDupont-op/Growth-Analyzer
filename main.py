from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
from concurrent.futures import ProcessPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for Windows asyncio loop with Playwright
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Startup Analyzer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AnalyzeRequest(BaseModel):
    url: str

def run_cli_scraper(url):
    # Force UTF-8 encoding for the subprocess environment
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
    print(f"DEBUG: Received request for {request.url}")
    logger.info(f"Received analysis request for: {request.url}")
    
    try:
        # Step 1: Scrape content
        print("DEBUG: Starting scraping in subprocess...")
        logger.info("Scraping content...")
        
        # Run scraping via CLI subprocess to ensure total isolation
        content = await asyncio.to_thread(run_cli_scraper, request.url)
            
        print("DEBUG: Scraping finished.")
        
        # Check for scraping errors
        if content.startswith("Erreur") or content.startswith("Une erreur"):
            raise HTTPException(status_code=400, detail=content)
            
        # Step 2: Analyze content
        print("DEBUG: Starting analysis...")
        logger.info("Analyzing content with Ollama...")
        analysis_result = await asyncio.to_thread(analyze_startup, content)
        print("DEBUG: Analysis finished.")
        
        if "error" in analysis_result:
             raise HTTPException(status_code=500, detail=analysis_result["error"])
             
        return analysis_result

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/download-pdf")
async def download_pdf_endpoint(data: dict):
    try:
        # Generate PDF
        filename = f"report_{int(time.time())}.pdf"
        create_pdf_report(data, filename)
        
        # Return file
        return FileResponse(filename, media_type='application/pdf', filename=filename)
    except Exception as e:
         logger.error(f"PDF generation error: {e}")
         raise HTTPException(status_code=500, detail=f"PDF Error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Startup Analyzer API is running. Use POST /analyze to analyze a startup."}
