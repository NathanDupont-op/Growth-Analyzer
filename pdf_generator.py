from fpdf import FPDF
import os
import urllib.request

FONT_URL = "https://github.com/Start9Labs/start-os/raw/master/backend/src/assets/fonts/DejaVuSans.ttf"
FONT_PATH = "DejaVuSans.ttf"

def ensure_font_exists():
    """Télécharge la police si elle n'est pas présente sur le serveur"""
    if not os.path.exists(FONT_PATH):
        print(f"Téléchargement de la police {FONT_PATH}...")
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        except Exception as e:
            print(f"Erreur téléchargement police: {e}")

class PDFReport(FPDF):
    def header(self):
        # use the no  risk police or helvetica
        if os.path.exists(FONT_PATH):
            self.set_font('DejaVu', '', 20)
        else:
            self.set_font('Helvetica', 'B', 20)
            
        self.cell(0, 10, 'GrowthAnalyzer Report', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        if os.path.exists(FONT_PATH):
            self.set_font('DejaVu', '', 8)
        else:
            self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def chapter_title(self, title):
        if os.path.exists(FONT_PATH):
            self.set_font('DejaVu', '', 16)
        else:
            self.set_font('Helvetica', 'B', 16)
            
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(4)

def create_pdf_report(data: dict, filename: str = "report.pdf") -> str:
    ensure_font_exists()
    
    pdf = PDFReport()
    
    if os.path.exists(FONT_PATH):
        pdf.add_font('DejaVu', '', FONT_PATH)
        pdf.set_font('DejaVu', '', 12)
    else:
        pdf.set_font('Helvetica', '', 12)
        
    pdf.add_page()
    
    def safe_str(text):
        if text is None: return ""
        return str(text)

    if os.path.exists(FONT_PATH):
        pdf.set_font('DejaVu', '', 24)
    else:
        pdf.set_font('Helvetica', 'B', 24)
        
    name = safe_str(data.get('name', 'Startup Analysis'))
    pdf.cell(0, 15, name, new_x="LMARGIN", new_y="NEXT", align='C')
    
    score = data.get('score_global', 0)
    
    if os.path.exists(FONT_PATH):
        pdf.set_font('DejaVu', '', 40)
    else:
        pdf.set_font('Helvetica', 'B', 40)
        
    if score >= 80:
        pdf.set_text_color(0, 200, 83) 
    elif score >= 50:
        pdf.set_text_color(255, 152, 0) 
    else:
        pdf.set_text_color(244, 67, 54) 
        
    pdf.cell(0, 20, f"{score}/100", new_x="LMARGIN", new_y="NEXT", align='C')
    
    pdf.set_text_color(0, 0, 0)
    if os.path.exists(FONT_PATH):
        pdf.set_font('DejaVu', '', 12)
    else:
        pdf.set_font('Helvetica', 'I', 12)
        
    pdf.cell(0, 10, "Growth Potential Score", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    pdf.chapter_title("Key Metrics")
    metrics = data.get('metrics', {})
    
    if os.path.exists(FONT_PATH):
        pdf.set_font('DejaVu', '', 12)
    else:
        pdf.set_font('Helvetica', '', 12)

    pdf.cell(50, 10, safe_str(f"Sector: {data.get('sector', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(50, 10, safe_str(f"Employees: {metrics.get('employees', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(50, 10, safe_str(f"Funding: {metrics.get('funding', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(50, 10, safe_str(f"Round: {metrics.get('round', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # 3. Strengths
    pdf.chapter_title("Strengths")
    for point in data.get('strengths', []):
        pdf.set_text_color(0, 128, 0)
        pdf.multi_cell(0, 8, f"+ {safe_str(point)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln()

    # 4. Weaknesses
    pdf.chapter_title("Weaknesses")
    for point in data.get('weaknesses', []):
        pdf.set_text_color(200, 0, 0)
        pdf.multi_cell(0, 8, f"- {safe_str(point)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln()

    output_path = os.path.join("/tmp", filename)
    
    pdf.output(output_path)
    return output_path 

