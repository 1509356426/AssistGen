import sys
import os
from pdfminer.high_level import extract_text

def extract_pdf_text(pdf_path, start_page=1, end_page=5):
    try:
        text = extract_text(pdf_path, page_numbers=range(start_page-1, end_page))
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_path> [start_page] [end_page]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_page = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    text = extract_pdf_text(pdf_path, start_page, end_page)
    print(text)