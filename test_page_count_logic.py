
from pypdf import PdfReader, PdfWriter
import io

def create_dummy_pdf(filename, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=100, height=100)
    
    with open(filename, "wb") as f:
        writer.write(f)
    print(f"Created {filename} with {pages} pages.")

def test_page_count_logic():
    # 1. Create dummy PDFs
    pdf1 = "test1.pdf"
    pdf2 = "test2.pdf"
    create_dummy_pdf(pdf1, 3)
    create_dummy_pdf(pdf2, 5)

    # 2. Simulate UploadedFile behavior (opened file object)
    with open(pdf1, "rb") as f1, open(pdf2, "rb") as f2:
        uploaded_files = [f1, f2]
        
        print("\n--- Testing Logic ---")
        for f in uploaded_files:
            try:
                # Logic added to ilovepdf.py
                reader = PdfReader(f)
                num_pages = len(reader.pages)
                print(f"[PDF] {f.name} ({num_pages} pages)")
                
                # Check current position (should be at end)
                # print(f"Position after read: {f.tell()}")
                
                # Reset file pointer
                f.seek(0)
                
                # Verify position
                if f.tell() != 0:
                     print(f"ERROR: File pointer not reset for {f.name}")
                else:
                     print(f"SUCCESS: File pointer reset for {f.name}")
                     
            except Exception as e:
                print(f"Error: {e}")

        # 3. Verify files are still readable for 'merging'
        print("\n--- Verifying Merge Readiness ---")
        merger = PdfWriter()
        try:
            for pdf in uploaded_files:
                merger.append(pdf)
            print("SUCCESS: Files successfully appended to merger.")
        except Exception as e:
            print(f"ERROR: Failed to append files to merger: {e}")

if __name__ == "__main__":
    test_page_count_logic()
