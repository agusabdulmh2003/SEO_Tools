import requests

def check_page_speed(url):
    try:
        # Cek kecepatan halaman menggunakan API pihak ketiga seperti PageSpeed Insights API
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}"
        response = requests.get(api_url)
        response.raise_for_status()

        # Mengambil data dari response JSON
        data = response.json()
        page_speed_score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0)

        return {"page_speed_score": page_speed_score}

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengakses PageSpeed API: {e}"}

def display_page_speed_info(url):
    page_speed_info = check_page_speed(url)
    if "error" in page_speed_info:
        return page_speed_info
    return {
        "url": url,
        "page_speed_info": page_speed_info
    }
