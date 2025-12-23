
import io
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image

def create_dummy_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

def test_standard_compression(pdf_bytes):
    print("Testing Standard Compression...")
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        
        writer.compress_identical_objects = True
        out = io.BytesIO()
        writer.write(out)
        print("Standard Compression: OK")
    except Exception as e:
        print(f"Standard Compression Failed: {e}")

def test_strong_compression(pdf_bytes):
    print("Testing Strong Compression...")
    try:
        # Check if poppler is installed by trying to convert
        # convert_from_bytes usually raises generic exceptions if poppler not found
        images = convert_from_bytes(pdf_bytes, dpi=72)
        if not images:
            print("Strong Compression: No images generated (Poppler issue?)")
            return

        image_list = []
        for img in images:
            img_byte_arr = io.BytesIO()
            img.convert('RGB').save(img_byte_arr, format='JPEG', quality=50)
            image_list.append(Image.open(img_byte_arr))
        
        if image_list:
            out = io.BytesIO()
            image_list[0].save(out, save_all=True, append_images=image_list[1:], format="PDF")
            print("Strong Compression: OK")
    except Exception as e:
        print(f"Strong Compression Failed (Likely Poppler missing or path issue): {e}")

if __name__ == "__main__":
    pdf_data = create_dummy_pdf()
    test_standard_compression(pdf_data)
    test_strong_compression(pdf_data)
