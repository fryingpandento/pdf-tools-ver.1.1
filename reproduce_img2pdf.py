
import requests
from io import BytesIO
from PIL import Image

def create_dummy_image():
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_img2pdf():
    url = "http://127.0.0.1:8000/api/image-to-pdf"
    
    img1 = create_dummy_image()
    img2 = create_dummy_image()
    
    files = [
        ('files', ('image1.jpg', img1, 'image/jpeg')),
        ('files', ('image2.jpg', img2, 'image/jpeg'))
    ]
    
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error Content: {response.content.decode()}")
        else:
            print("Success: PDF generated (size: {} bytes)".format(len(response.content)))
            with open("output_test.pdf", "wb") as f:
                f.write(response.content)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_img2pdf()
