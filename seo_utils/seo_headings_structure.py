import requests
from bs4 import BeautifulSoup

def check_headings_structure(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Menemukan semua heading
        headings = {
            "h1": len(soup.find_all('h1')),
            "h2": len(soup.find_all('h2')),
            "h3": len(soup.find_all('h3')),
            "h4": len(soup.find_all('h4')),
            "h5": len(soup.find_all('h5')),
            "h6": len(soup.find_all('h6')),
        }

        return headings

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengakses URL: {e}"}

def display_headings_structure_info(url):
    headings_info = check_headings_structure(url)
    if "error" in headings_info:
        return headings_info
    return {
        "url": url,
        "headings_info": headings_info
    }
