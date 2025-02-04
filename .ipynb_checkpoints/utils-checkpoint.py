import os
import re
from PyPDF2 import PdfReader
import pandas as pd
from fpdf import FPDF
from process import process_url  # Daha önce yazdığınız link işleme kodu

def extract_links_from_pdf(file_path):
    """PDF dosyasından linkleri çıkar."""
    links = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        text = page.extract_text()
        links.extend(re.findall(r'https?://\S+', text))
    return links

def extract_links_from_excel(file_path):
    """Excel dosyasından linkleri çıkar."""
    df = pd.read_excel(file_path)
    links = []
    for column in df.columns:
        links.extend(df[column].dropna().astype(str).str.extract(r'(https?://\S+)')[0].dropna().tolist())
    return links

def process_links_from_file(file_path, output_dir):
    """PDF veya Excel dosyasındaki linkleri işleyip sonuç PDF'si oluştur."""
    if file_path.endswith(".pdf"):
        links = extract_links_from_pdf(file_path)
    elif file_path.endswith(".xlsx"):
        links = extract_links_from_excel(file_path)
    else:
        raise ValueError("Desteklenmeyen dosya formatı.")

    # Her bir linki işleyip sonuçları PDF'e kaydet
    output_pdf = os.path.join(output_dir, "results.pdf")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for url in links:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"URL: {url}\n")
        
        try:
            # Linki işleyip özetle
            summary, tfidf_image, lda_image = process_url(url)
            pdf.multi_cell(0, 10, f"Summary:\n{summary}\n")
            pdf.image(tfidf_image, x=10, y=80, w=190)
            pdf.add_page()
            pdf.image(lda_image, x=10, y=80, w=190)
        except Exception as e:
            pdf.multi_cell(0, 10, f"Link işlenirken hata oluştu: {str(e)}\n")

    pdf.output(output_pdf)
    return output_pdf
