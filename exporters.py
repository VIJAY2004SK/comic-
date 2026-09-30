import os
from datetime import datetime
from fpdf import FPDF

EXPORT_FOLDER = "static/exports"

class ComicPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'ComicCraft AI Generated Story', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

def save_pdf(layout: list) -> str:
    """
    Compiles comic panels into a structured PDF document.
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        
        # Title
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, f"Panel {panel['panel']}: {panel['title']}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(2)

        # Image
        image_path = panel['image_path']
        if os.path.exists(image_path):
            # Centered image rendering
            pdf.image(image_path, x=35, y=pdf.get_y(), w=140)
            pdf.set_y(pdf.get_y() + 145)
        else:
            pdf.set_font('helvetica', 'I', 10)
            pdf.cell(0, 10, f"[Image Missing: {image_path}]", new_x="LMARGIN", new_y="NEXT")

        # Text Content
        pdf.set_font('helvetica', '', 10)
        clean_text = panel['text'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_text)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_path)

    return pdf_path