from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader, PdfWriter
import zipfile
import io
import os

app = FastAPI()

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoint: Split PDF
@app.post("/api/split")
async def split_pdf(
    file: UploadFile = File(...),
    splitOption: str = Form(...),
    # For custom range, we might receive it as a form field or not
    # We'll expect it if splitOption is 'custom'
    # However, to keep signature simple, we can fetch it from kwargs or make it optional form
):
    try:
        # Read file into memory
        file_bytes = await file.read()
        file_io = io.BytesIO(file_bytes)
        reader = PdfReader(file_io)
        total_pages = len(reader.pages)
        
        output_zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(output_zip_buffer, "w") as zf:
            if splitOption == 'all':
                # Split all pages
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    pdf_bytes = io.BytesIO()
                    writer.write(pdf_bytes)
                    zf.writestr(f"page_{i+1}.pdf", pdf_bytes.getvalue())
            
            elif splitOption == 'custom':
                # TODO: Implement custom range logic if needed
                # For this prototype, we'll default to 'all' or simple logic
                # Since we didn't add the input field for 'custom' in the React form definitively yet,
                # let's just do all for now or error.
                # Ideally we receive a 'range' param.
                pass

        # Return the ZIP file
        return Response(
            content=output_zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=split_files.zip"}
        )

    except Exception as e:
        return Response(content=str(e), status_code=500)

@app.post("/api/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    try:
        merger = PdfWriter()
        for file in files:
            file_bytes = await file.read()
            file_io = io.BytesIO(file_bytes)
            merger.append(file_io)
            
        output_buffer = io.BytesIO()
        merger.write(output_buffer)
        merger.close()
        
        return Response(
            content=output_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=merged.pdf"}
        )
    except Exception as e:
        return Response(content=str(e), status_code=500)

@app.post("/api/reorder")
async def reorder_pdf(
    file: UploadFile = File(...),
    order: str = Form(...) # "1,3,2"
):
    try:
        file_bytes = await file.read()
        file_io = io.BytesIO(file_bytes)
        reader = PdfReader(file_io)
        writer = PdfWriter()
        
        # Parse order string "1, 3, 2" -> [0, 2, 1] (0-indexed)
        try:
            page_indices = [int(x.strip()) - 1 for x in order.split(",") if x.strip()]
        except ValueError:
             return Response(content="Invalid order format", status_code=400)

        for idx in page_indices:
            if 0 <= idx < len(reader.pages):
                writer.add_page(reader.pages[idx])
        
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        
        return Response(
            content=output_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reordered.pdf"}
        )
    except Exception as e:
         return Response(content=str(e), status_code=500)

from pdf2image import convert_from_bytes
from PIL import Image

@app.post("/api/pdf-to-image")
async def pdf_to_image(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        images = convert_from_bytes(file_bytes)
        
        output_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(output_zip_buffer, "w") as zf:
            for i, img in enumerate(images):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                zf.writestr(f"page_{i+1}.jpg", img_byte_arr.getvalue())
                
        return Response(
            content=output_zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=pdf_images.zip"}
        )
    except Exception as e:
         return Response(content=str(e), status_code=500)

@app.post("/api/image-to-pdf")
async def image_to_pdf(files: list[UploadFile] = File(...)):
    try:
        image_list = []
        for file in files:
            file_bytes = await file.read()
            img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
            image_list.append(img)
            
        if not image_list:
             return Response(content="No images provided", status_code=400)
             
        pdf_bytes = io.BytesIO()
        image_list[0].save(
            pdf_bytes, 
            save_all=True, 
            append_images=image_list[1:], 
            format="PDF"
        )
        
        return Response(
            content=pdf_bytes.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=images.pdf"}
        )
    except Exception as e:
         return Response(content=str(e), status_code=500)

@app.post("/api/protect")
async def protect_pdf(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    try:
        file_bytes = await file.read()
        file_io = io.BytesIO(file_bytes)
        reader = PdfReader(file_io)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password)
        
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        
        return Response(
            content=output_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=protected.pdf"}
        )
    except Exception as e:
         return Response(content=str(e), status_code=500)

    except Exception as e:
         return Response(content=str(e), status_code=500)

from pypdf import Transformation, PageObject

@app.post("/api/n-up")
async def n_up_pdf(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        file_io = io.BytesIO(file_bytes)
        reader = PdfReader(file_io)
        writer = PdfWriter()
        
        pages = reader.pages
        num_pages = len(pages)
        
        # Process in chunks of 4
        for i in range(0, num_pages, 4):
            # Take geometry from first page in chunk
            base_page = pages[i]
            width = float(base_page.mediabox.width)
            height = float(base_page.mediabox.height)
            
            # Create blank page
            new_page = PageObject.create_blank_page(width=width, height=height)
            
            chunk = pages[i:i+4]
            
            # Positions (2x2 Grid)
            # 1: TL (0, h/2) | 2: TR (w/2, h/2)
            # 3: BL (0, 0)   | 4: BR (w/2, 0)
            target_positions = [
                (0, height/2),      # Top-Left
                (width/2, height/2),# Top-Right
                (0, 0),             # Bottom-Left
                (width/2, 0)        # Bottom-Right
            ]
            
            for j, page in enumerate(chunk):
                # Ensure page box is consistent (handling mixed orientations is complex, assuming consistent for now)
                # Scale 0.5
                op = Transformation().scale(0.5, 0.5).translate(tx=target_positions[j][0], ty=target_positions[j][1])
                page.add_transformation(op)
                # Merge transformed page onto blank page
                new_page.merge_page(page)
            
            writer.add_page(new_page)
            
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        
        return Response(
            content=output_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=nup_4in1.pdf"}
        )
    except Exception as e:
         return Response(content=str(e), status_code=500)

# Serve the React Frontend (Static Files)
# We assume the frontend/index.html is the entry point
# We can map "/" to index.html directly or serve the directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
