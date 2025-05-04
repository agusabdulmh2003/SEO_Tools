# main.py
import requests
from bs4 import BeautifulSoup
from seo_utils import (
    meta_checker,
    url_checker,
    link_checker,
    mobile_checker,
    schema_checker,
    content_checker,
    security_checker,
)

def run_seo_analysis(url):
    print(f"Analyzing: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        meta_checker.check_meta(soup)
        url_checker.analyze_url(url)
        link_checker.check_redirects_and_broken_links(url, soup)
        mobile_checker.check_mobile_friendly(soup)
        schema_checker.check_structured_data(soup)
        content_checker.analyze_content(soup)
        security_checker.check_security(url)

    except Exception as e:
        print(f"❌ Gagal memuat halaman: {e}")

if __name__ == "__main__":
    url_input = input("Masukkan URL: ")
    run_seo_analysis(url_input)
