
import requests
from io import BytesIO
from PIL import Image

def create_text_file():
    return BytesIO(b"This is not an image")

def test_img2pdf():
    url = "http://127.0.0.1:8000/api/image-to-pdf"
    
    print("Testing Text File...")
    img1 = create_text_file()
    
    files = [
        ('files', ('not_image.txt', img1, 'text/plain'))
    ]
    
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error Content: {response.content.decode()}")
        else:
            print("Success: PDF generated (size: {} bytes)".format(len(response.content)))
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_img2pdf()
