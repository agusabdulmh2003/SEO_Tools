import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hilangkan skrip dan style
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        
        text = soup.get_text(separator=' ')
        return re.sub(r'\s+', ' ', text.strip())
    except Exception as e:
        return None

def calculate_keyword_density(url, top_n=10):
    text = get_text_from_url(url)
    if not text:
        return {"error": "Gagal mengambil konten dari URL"}

    # Ubah ke huruf kecil dan ambil kata-kata
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Hitung frekuensi kata
    word_counts = Counter(words)
    total_words = sum(word_counts.values())

    # Ambil top_n kata terbanyak (tanpa stopwords agar lebih akurat nanti bisa ditambahkan filter)
    top_keywords = word_counts.most_common(top_n)
    
    density_result = []
    for keyword, count in top_keywords:
        density = (count / total_words) * 100
        density_result.append({
            "keyword": keyword,
            "count": count,
            "density": round(density, 2)
        })

    return {
        "url": url,
        "total_words": total_words,
        "top_keywords": density_result
    }
