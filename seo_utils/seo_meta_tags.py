import requests
from bs4 import BeautifulSoup

def check_meta_tags(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Menemukan meta tags
        meta_tags = {
            "title": soup.title.string if soup.title else None,
            "description": None,
            "keywords": None
        }

        # Mencari meta description dan keywords
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})

        if meta_description:
            meta_tags["description"] = meta_description.get('content')
        if meta_keywords:
            meta_tags["keywords"] = meta_keywords.get('content')

        return meta_tags

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengakses URL: {e}"}

def display_meta_tags_info(url):
    meta_tags_info = check_meta_tags(url)
    if "error" in meta_tags_info:
        return meta_tags_info
    return {
        "url": url,
        "meta_tags_info": meta_tags_info
    }
