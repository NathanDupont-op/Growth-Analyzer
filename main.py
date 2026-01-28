from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
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

# Configuration des Templates
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
    print(f"DEBUG: Received request for {request.url}")
    logger.info(f"Received analysis request for: {request.url}")
    start_total = time.time()
    
    # Check removed as user hardcoded key in analyzer.py
    # if not os.environ.get("GROQ_API_KEY"): ...

    try:
        # Step 1: Scrape content
        print("DEBUG: Starting scraping in subprocess...")
        t0 = time.time()
        
        # Run scraping via CLI subprocess to ensure total isolation
        content = await asyncio.to_thread(run_cli_scraper, request.url)
        
        t1 = time.time()
        print(f"DEBUG: Scraping finished in {t1 - t0:.2f}s. Content length: {len(content) if content else 0} chars")
        
        # Check for scraping errors
        if not content:
            raise HTTPException(status_code=400, detail="Scraping returned empty content.")

        if content.startswith("Erreur") or content.startswith("Une erreur"):
            raise HTTPException(status_code=400, detail=content)
            
        # Step 2: Analyze content
        print("DEBUG: Starting analysis with Groq...")
        t2 = time.time()
        analysis_result = await asyncio.to_thread(analyze_startup, content)
        t3 = time.time()
        print(f"DEBUG: Analysis finished in {t3 - t2:.2f}s.")
        
        if "error" in analysis_result:
             logger.error(f"Analysis error: {analysis_result['error']}")
             raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        print(f"DEBUG: Total request time: {time.time() - start_total:.2f}s")
        return analysis_result

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/download-pdf")
async def download_pdf_endpoint(data: dict):
    try:
        filename = f"report_{int(time.time())}.pdf"
        file_path = create_pdf_report(data, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="PDF generated but file not found on server.")
            
        return FileResponse(
            path=file_path, 
            media_type='application/pdf', 
            filename=filename
        )
    except Exception as e:
         logger.error(f"PDF generation error: {e}")
         raise HTTPException(status_code=500, detail=f"PDF Error: {str(e)}")

@app.get("/")
async def read_root(request: Request):
    # Au lieu de retourner du JSON, on retourne le fichier HTML
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

