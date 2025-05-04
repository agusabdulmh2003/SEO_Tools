import requests
from bs4 import BeautifulSoup

def check_meta_tags(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.title.string if soup.title else "Title tag not found"
        description = soup.find("meta", attrs={"name": "description"})
        description_content = description["content"] if description else "Meta description not found"

        return {
            "title": title,
            "description": description_content
        }

    except Exception as e:
        return {"error": str(e)}
