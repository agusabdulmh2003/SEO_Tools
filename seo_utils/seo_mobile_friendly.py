import requests

def check_mobile_friendly(url):
    try:
        # Cek apakah halaman mobile-friendly menggunakan Google Mobile-Friendly API
        api_url = f"https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run?url={url}"
        response = requests.get(api_url)
        response.raise_for_status()

        # Mengambil data dari response JSON
        data = response.json()
        mobile_friendly = data.get("mobileFriendliness", "")

        return {"mobile_friendly": mobile_friendly}

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengakses Mobile-Friendly API: {e}"}

def display_mobile_friendly_info(url):
    mobile_friendly_info = check_mobile_friendly(url)
    if "error" in mobile_friendly_info:
        return mobile_friendly_info
    return {
        "url": url,
        "mobile_friendly_info": mobile_friendly_info
    }
