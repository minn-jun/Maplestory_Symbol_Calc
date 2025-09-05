import requests
import io
from PIL import Image, ImageTk

def fetch_and_crop_character_image(url):
    """URL에서 이미지를 가져와 캐릭터 중심으로 크롭하고 Tkinter용 이미지 객체로 변환합니다."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        image_data = Image.open(io.BytesIO(response.content))
        
        # 원본 이미지 크기: 300x300
        # (left, top, right, bottom)
        crop_box = (150 - 45, 200 - 85, 150 + 45, 200 + 5)
        
        cropped_image = image_data.crop(crop_box)
        
        # GUI에 표시할 크기로 리사이즈
        resized_image = cropped_image.resize((96, 96), Image.Resampling.LANCZOS)
        
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        print(f"이미지 처리 오류: {e}")
        return None