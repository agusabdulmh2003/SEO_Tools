import requests
from bs4 import BeautifulSoup

def check_image_alt_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cari semua gambar dan periksa alt text
        images = soup.find_all('img')
        images_with_alt = []
        images_without_alt = []

        for img in images:
            alt_text = img.get('alt', '').strip()
            if alt_text:
                images_with_alt.append(alt_text)
            else:
                images_without_alt.append(f"Image src: {img.get('src')}")

        return {
            "images_with_alt_text": images_with_alt,
            "images_without_alt_text": images_without_alt,
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengakses URL: {e}"}

def display_image_alt_text_info(url):
    alt_text_info = check_image_alt_text(url)
    if "error" in alt_text_info:
        return alt_text_info
    return {
        "url": url,
        "alt_text_info": {
            "images_with_alt_text": alt_text_info["images_with_alt_text"],
            "images_without_alt_text": alt_text_info["images_without_alt_text"]
        }
    }
