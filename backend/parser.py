import io
import tempfile
import os
import pdfplumber
from PyPDF2 import PdfReader
import docx2txt

def extract_text_from_pdf(file_bytes):
    """
    Extracts text from PDF bytes using pdfplumber as primary and PyPDF2 as fallback.
    """
    text = ""
    # Try pdfplumber first (cleaner text formatting)
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If text is extracted, return it
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"pdfplumber extraction failed: {str(e)}. Trying PyPDF2...")
    
    # Fallback to PyPDF2
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(file_bytes):
    """
    Extracts text from DOCX bytes using docx2txt.
    """
    try:
        # docx2txt is most reliable with an actual file path, so stage bytes to a temp file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            text = docx2txt.process(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from Word Document: {str(e)}")

def extract_text(file_name, file_bytes):
    """
    General function that detects extension and extracts text.
    """
    ext = file_name.split(".")[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    elif ext == "doc":
        raise ValueError("Unsupported file format. Please convert .doc files to .docx before uploading.")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
