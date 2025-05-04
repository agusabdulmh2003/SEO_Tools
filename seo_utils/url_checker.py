import tldextract

def analyze_url(url):
    print("\n🔗 URL Analysis")
    ext = tldextract.extract(url)
    path = url.split(ext.domain + "." + ext.suffix)[-1]
    
    if len(path) > 100:
        print("⚠️ URL terlalu panjang.")
    if "_" in url:
        print("⚠️ Gunakan '-' daripada '_' di URL.")
    if ext.domain not in url:
        print("⚠️ URL tidak mengandung domain utama.")
    
    print(f"URL Path: {path}")
