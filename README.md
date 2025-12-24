# PDF Tools (React + FastAPI)

A modern, mobile-friendly PDF manipulation tool built with **React** (Frontend) and **FastAPI** (Backend).

## Features
- **Split**: Specific pages or extraction.
- **Merge**: Combine multiple PDFs.
- **Reorder**: Change page order interactively.
- **Conversions**: PDF to Image, Image to PDF.
- **Security**: Add password protection.
- **4-in-1**: Combine 4 pages into 1 (N-up layout).

## Architecture
- **Frontend**: Single HTML file (`frontend/index.html`) using React, Tailwind CSS, and Lucide Icons via CDN. No build step required.
- **Backend**: Python FastAPI (`api.py`) handling PDF logic with `pypdf` and `pdf2image`.

## How to Run Locally

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start Server**:
    ```bash
    uvicorn api:app --reload
    ```

3.  **Access App**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## Deployment (Render)
This project is configured for deployment on Render via Docker.
- `Dockerfile`: Configured to run `uvicorn`.
- `render.yaml`: Deployment configuration.

## Legacy
- `ilovepdf.py`: Old Streamlit version (deprecated).
