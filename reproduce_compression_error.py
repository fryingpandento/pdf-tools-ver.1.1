
from pypdf import PdfReader, PdfWriter
import io

def create_test_pdf(filename):
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(filename, "wb") as f:
        writer.write(f)

def reproduce_error():
    filename = "repro_test.pdf"
    create_test_pdf(filename)
    
    print("--- Attempting Reproduction ---")
    try:
        reader = PdfReader(filename)
        writer = PdfWriter()
        
        # Logic from ilovepdf.py
        for page in reader.pages:
            page.compress_content_streams() # Potentially problematic line
            writer.add_page(page)
        
        writer.compress_identical_objects = True # Potentially problematic line
        
        out = io.BytesIO()
        writer.write(out)
        print("Success! No error raised.")
        
    except Exception as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    reproduce_error()
