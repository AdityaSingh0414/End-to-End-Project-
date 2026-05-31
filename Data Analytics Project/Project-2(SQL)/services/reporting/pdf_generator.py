import pandas as pd
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_csv(df, filename):
    path = os.path.join("reports", "generated_csvs", f"{filename}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return path

def generate_excel(df, filename):
    path = os.path.join("reports", "generated_excels", f"{filename}.xlsx")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_excel(path, index=False)
    return path

def generate_pdf(summary_text, filename):
    path = os.path.join("reports", "generated_pdfs", f"{filename}.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = canvas.Canvas(path, pagesize=letter)
    c.drawString(100, 750, "Executive Summary Report")
    c.drawString(100, 730, "-" * 50)
    
    y = 700
    for line in summary_text.split('\n'):
        c.drawString(100, y, line[:100]) # Basic wrapping
        y -= 20
        
    c.save()
    return path
