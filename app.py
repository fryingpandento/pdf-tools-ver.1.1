from flask import Flask, render_template, request, send_file, jsonify
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image
import io
import zipfile
import os

app = Flask(__name__)

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/split', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        mode = request.form.get('mode') # 'all' or 'range'
        range_input = request.form.get('range', '')

        reader = PdfReader(file)
        total_pages = len(reader.pages)
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zf:
            if mode == 'all':
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    pdf_bytes = io.BytesIO()
                    writer.write(pdf_bytes)
                    zf.writestr(f"page_{i+1}.pdf", pdf_bytes.getvalue())
            
            elif mode == 'range':
                if not range_input:
                    return jsonify({'error': 'Range input is empty'}), 400
                
                parts = [p.strip() for p in range_input.split(',')]
                files_created = 0
                
                for part in parts:
                    writer = PdfWriter()
                    filename = ""
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        original_start, original_end = start, end
                        # Adjust for 0-index and bounds
                        start = max(1, start)
                        end = min(total_pages, end)
                        
                        if start > end: continue # Invalid range

                        for i in range(start - 1, end):
                            writer.add_page(reader.pages[i])
                        filename = f"pages_{original_start}-{original_end}.pdf"
                    else:
                        try:
                            p_num = int(part)
                            if 1 <= p_num <= total_pages:
                                writer.add_page(reader.pages[p_num - 1])
                                filename = f"page_{p_num}.pdf"
                        except ValueError:
                            continue # Ignore non-integer parts

                    if len(writer.pages) > 0 and filename:
                        pdf_bytes = io.BytesIO()
                        writer.write(pdf_bytes)
                        zf.writestr(filename, pdf_bytes.getvalue())
                        files_created += 1
                
                if files_created == 0:
                     return jsonify({'error': 'No valid pages found to split'}), 400

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='split_files.zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/merge', methods=['POST'])
def merge_pdf():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
             return jsonify({'error': 'No files selected'}), 400

        merger = PdfWriter()
        for pdf in files:
            merger.append(pdf)
        
        output_buffer = io.BytesIO()
        merger.write(output_buffer)
        merger.close()
        output_buffer.seek(0)

        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reorder', methods=['POST'])
def reorder_pdf():
    try:
        if 'file' not in request.files:
             return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        order_str = request.form.get('order') # e.g. "1,3,2"

        if not order_str:
            return jsonify({'error': 'No order specified'}), 400

        reader = PdfReader(file)
        total_pages = len(reader.pages)
        writer = PdfWriter()

        try:
            order_list = [int(p.strip()) for p in order_str.split(',') if p.strip()]
        except ValueError:
            return jsonify({'error': 'Invalid format for order'}), 400

        for p_num in order_list:
            if 1 <= p_num <= total_pages:
                writer.add_page(reader.pages[p_num - 1])
            else:
                 return jsonify({'error': f'Page number {p_num} out of range'}), 400
        
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reordered.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf-to-img', methods=['POST'])
def pdf_to_img():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        file_bytes = file.read() # pdf2image needs bytes or path

        # Convert to images
        images = convert_from_bytes(file_bytes)
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for i, img in enumerate(images):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                zf.writestr(f"page_{i+1}.jpg", img_byte_arr.getvalue())
        
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='pdf_images.zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/img-to-pdf', methods=['POST'])
def img_to_pdf():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
             return jsonify({'error': 'No files selected'}), 400

        image_list = []
        for img_file in files:
            image = Image.open(img_file).convert('RGB')
            image_list.append(image)
        
        if not image_list:
             return jsonify({'error': 'No valid images found'}), 400

        pdf_bytes = io.BytesIO()
        image_list[0].save(pdf_bytes, save_all=True, append_images=image_list[1:], format="PDF")
        pdf_bytes.seek(0)

        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='images.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/encrypt', methods=['POST'])
def encrypt_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        password = request.form.get('password')

        if not password:
            return jsonify({'error': 'No password provided'}), 400

        reader = PdfReader(file)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)
        
        writer.encrypt(password)
        
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='protected.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # --- ngrok Setup ---
    import os
    # Check if running on Render (or other cloud env)
    if os.environ.get('RENDER') or os.environ.get('DYNO'):
        # Production mode
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Local development with ngrok
        try:
            from pyngrok import ngrok
            
            # Open a HTTP tunnel on the default port 5000
            public_url = ngrok.connect(5000).public_url
            print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000\"".format(public_url))
            print(" * Public URL:", public_url)
        except Exception as e:
            print(f" * Could not start ngrok: {e}")
            print(" * Running locally only.")
        app.run(debug=True, port=5000)
