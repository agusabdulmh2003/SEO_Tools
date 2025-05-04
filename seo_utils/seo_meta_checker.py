import requests
from bs4 import BeautifulSoup

def get_meta_tags(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil tag meta
        meta_tags = {
            "title": soup.title.string if soup.title else "Tidak ada judul",
            "description": "",
            "keywords": "",
        }

        # Mencari meta tag description dan keywords
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'description':
                meta_tags["description"] = meta.get('content', 'Tidak ada deskripsi')
            elif meta.get('name') == 'keywords':
                meta_tags["keywords"] = meta.get('content', 'Tidak ada kata kunci')

        return meta_tags

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengakses URL: {e}"}

def check_meta_info(url):
    meta_data = get_meta_tags(url)
    if "error" in meta_data:
        return meta_data
    return {
        "url": url,
        "meta_info": {
            "title": meta_data["title"],
            "description": meta_data["description"],
            "keywords": meta_data["keywords"]
        }
    }
