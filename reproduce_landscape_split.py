from pypdf import PdfWriter, PdfReader
import io

def create_landscape_pdf():
    writer = PdfWriter()
    # Create a blank landscape page (A4 Landscape: 842 x 595)
    writer.add_blank_page(width=842, height=595)
    writer.add_blank_page(width=842, height=595)
    writer.add_blank_page(width=842, height=595)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def test_split_logic():
    print("Creating landscape PDF...")
    pdf_file = create_landscape_pdf()
    
    reader = PdfReader(pdf_file)
    print(f"Total pages: {len(reader.pages)}")
    print(f"Page 1 size: {reader.pages[0].mediabox}")
    
    # Simulate processing '1-2'
    print("Attempting to split pages 1-2...")
    try:
        writer = PdfWriter()
        for i in range(0, 2):
            writer.add_page(reader.pages[i])
        
        out_buf = io.BytesIO()
        writer.write(out_buf)
        print(f"Success. Output size: {len(out_buf.getvalue())} bytes")
        
        # Check output orientation
        out_buf.seek(0)
        out_reader = PdfReader(out_buf)
        print(f"Output Page 1 size: {out_reader.pages[0].mediabox}")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_split_logic()
