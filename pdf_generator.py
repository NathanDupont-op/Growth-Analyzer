from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 10, 'GrowthAnalyzer Report', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 12)
        # Encode/Decode to handle latin-1 compatible chars, replace others to avoid crash
        safe_body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 8, safe_body)
        self.ln()

def create_pdf_report(data: dict, filename: str = "report.pdf") -> str:
    pdf = PDFReport()
    pdf.add_page()
    
    # Safe text helper
    def safe_text(text):
        if not text: return ""
        if not isinstance(text, str): text = str(text)
        # Replace common markdown/unicode arrows/bullets that crash latin-1
        text = text.replace('→', '->').replace('•', '-')
        return text.encode('latin-1', 'replace').decode('latin-1')

    # 1. Title & Score
    pdf.set_font('Helvetica', 'B', 24)
    name = safe_text(data.get('name', 'Startup Analysis'))
    pdf.cell(0, 15, name, new_x="LMARGIN", new_y="NEXT", align='C')
    
    score = data.get('score_global', 0)
    pdf.set_font('Helvetica', 'B', 40)
    if score >= 80:
        pdf.set_text_color(0, 200, 83) 
    elif score >= 50:
        pdf.set_text_color(255, 152, 0) 
    else:
        pdf.set_text_color(244, 67, 54) 
        
    pdf.cell(0, 20, f"{score}/100", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'I', 12)
    pdf.cell(0, 10, "Growth Potential Score", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    # 2. Metrics Grid
    pdf.chapter_title("Key Metrics")
    metrics = data.get('metrics', {})
    
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(50, 10, safe_text(f"Sector: {data.get('sector', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(50, 10, safe_text(f"Employees: {metrics.get('employees', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(50, 10, safe_text(f"Funding: {metrics.get('funding', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(50, 10, safe_text(f"Round: {metrics.get('round', '-')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # 3. Strengths
    pdf.chapter_title("Strengths")
    for point in data.get('strengths', []):
        pdf.set_text_color(0, 128, 0)
        # Force return to left margin after multi_cell
        pdf.multi_cell(0, 8, f"+ {safe_text(point)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln()

    # 4. Weaknesses
    pdf.chapter_title("Weaknesses")
    for point in data.get('weaknesses', []):
        pdf.set_text_color(200, 0, 0)
        pdf.multi_cell(0, 8, f"- {safe_text(point)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln()

    pdf.output(filename)
    return filename
