from pypdf import PdfWriter, PdfReader, PageObject, Transformation
import io

def create_rotated_pdf():
    writer = PdfWriter()
    # Create Portrait pages, rotated 90 degrees
    for i in range(4):
        # A4 Portrait: 595 x 842
        page = writer.add_blank_page(width=595, height=842)
        page.rotate(90)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def test_nup_logic():
    print("Creating ROTATED landscape PDF...")
    pdf_file = create_rotated_pdf()
    
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    
    pages = reader.pages
    
    # Logic fix
    base_page = pages[0]
    
    # Check rotation
    rotation = base_page.get("/Rotate", 0)
    width = float(base_page.mediabox.width)
    height = float(base_page.mediabox.height)
    
    if rotation in [90, 270]:
        width, height = height, width
        
    print(f"Base dimensions (Corrected): {width} x {height}")
    
    new_page = PageObject.create_blank_page(width=width, height=height)
    
    chunk = pages[0:4]
    
    target_positions = [
        (0, height/2),      # TL
        (width/2, height/2),# TR
        (0, 0),             # BL
        (width/2, 0)        # BR
    ]
    
    print("Target Positions:", target_positions)
    
    for j, page in enumerate(chunk):
        # We process pages in user logic
        # If the page is rotated, we might need to handle it.
        # But if we just merge, hopefully pypdf handles it.
        
        # NOTE: pypdf transformation applies to the content stream.
        # If content is 595x842 but Rot=90, visually it's 842x595.
        # If we place it on 842x595 canvas:
        # We want to scale it to 0.5.
        
        op = Transformation().scale(0.5, 0.5).translate(tx=target_positions[j][0], ty=target_positions[j][1])
        page.add_transformation(op)
        new_page.merge_page(page)
    
    writer.add_page(new_page)
    
    out_buf = io.BytesIO()
    writer.write(out_buf)
    print(f"Success. Output size: {len(out_buf.getvalue())} bytes")
    
    # Verify output
    out_buf.seek(0)
    out_reader = PdfReader(out_buf)
    print(f"Output Page 1 size: {out_reader.pages[0].mediabox}")

if __name__ == "__main__":
    test_nup_logic()
