
from pypdf import PdfReader, PdfWriter
import io

def create_complex_pdf(filename):
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    # Add some data to content stream
    page = writer.pages[0]
    # This is a hack to add content, but for testing we just need *some* stream
    # Real PDFs have streams.
    with open(filename, "wb") as f:
        writer.write(f)

def test_add_then_compress():
    filename = "test_strategy.pdf"
    create_complex_pdf(filename)
    
    print("--- Testing Strategy: Add then Compress ---")
    try:
        reader = PdfReader(filename)
        writer = PdfWriter()
        
        for page in reader.pages:
            # New Strategy: Add first, then compress the writer's copy
            writer.add_page(page)
            writer.pages[-1].compress_content_streams()
        
        # We disabled this locally, but let's test without it first as user said "still failing"
        # writer.compress_identical_objects = True 
        
        out = io.BytesIO()
        writer.write(out)
        print("Success! Strategy worked.")
        
    except Exception as e:
        print(f"Strategy Failed: {e}")

if __name__ == "__main__":
    test_add_then_compress()
