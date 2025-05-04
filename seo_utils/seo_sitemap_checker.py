import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def check_sitemap(url):
    sitemap_urls = [
        urljoin(url, "/sitemap.xml"),
        urljoin(url, "/sitemap_index.xml"),
        urljoin(url, "/sitemap-index.xml"),
    ]

    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200 and ("<urlset" in response.text or "<sitemapindex" in response.text):
                soup = BeautifulSoup(response.content, "xml")
                urls = [loc.text for loc in soup.find_all("loc")]
                return {
                    "sitemap_url": sitemap_url,
                    "found": True,
                    "url_count": len(urls),
                    "sample_urls": urls[:5]  # Hanya tampilkan 5 contoh URL pertama
                }
        except requests.exceptions.RequestException:
            continue

    return {
        "sitemap_url": None,
        "found": False,
        "url_count": 0,
        "sample_urls": []
    }
