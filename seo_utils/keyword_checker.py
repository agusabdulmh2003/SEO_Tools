import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

def check_keywords(url, keywords):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text().lower()

        words = re.findall(r'\b\w+\b', text)
        word_count = Counter(words)

        keyword_results = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_results[keyword] = word_count.get(keyword_lower, 0)

        return keyword_results

    except Exception as e:
        return {"error": str(e)}
