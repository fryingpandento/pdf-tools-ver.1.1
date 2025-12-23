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

# Serve the React Frontend (Static Files)
# We assume the frontend/index.html is the entry point
# We can map "/" to index.html directly or serve the directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
