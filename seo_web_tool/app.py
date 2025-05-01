from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>SEO Analysis Tool</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; background: #f5f5f5; }
        h1 { color: #2c3e50; }
        form { margin-bottom: 2em; background: white; padding: 1em; border-radius: 5px; }
        label { display: block; margin-bottom: 0.5em; font-weight: bold; }
        input[type="text"], input[type="url"] { width: 100%; padding: 0.5em; margin-bottom: 1em; }
        button { background-color: #2980b9; color: white; border: none; padding: 0.7em 1.2em; cursor: pointer; border-radius: 4px; }
        button:hover { background-color: #3498db; }
        .result { background: white; padding: 1em; border-radius: 5px; box-shadow: 0 0 10px #bbb; }
        table { border-collapse: collapse; width: 100%; max-width: 600px; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #2980b9; color: white; }
        .note { font-size: 0.9em; color: #555; margin-top: 1em; }
        a { color: #2980b9; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .error { color: red; margin-top: 1em; font-weight: bold; }
    </style>
</head>
<body>
    <h1>SEO Analysis Tool</h1>
    <form method="post">
        <label for="url">URL yang ingin dianalisis:</label>
        <input type="url" id="url" name="url" placeholder="https://example.com" required value="{{ url|default('') }}">
        <label for="keyword">Kata kunci (opsional):</label>
        <input type="text" id="keyword" name="keyword" placeholder="Masukkan kata kunci" value="{{ keyword|default('') }}">
        <button type="submit">Analisis SEO</button>
    </form>

    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}

    {% if seo_result %}
    <div class="result">
        <h2>Hasil Analisis SEO untuk <a href="{{ url }}" target="_blank">{{ url }}</a></h2>
        <p><strong>Waktu muat halaman:</strong> {{ load_time }} detik</p>
        <table>
            <tr><th>Judul Halaman (Title)</th><td>{{ seo_result.title }}</td></tr>
            <tr><th>Meta Deskripsi</th><td>{{ seo_result.meta_description }}</td></tr>
        </table>
        <h3>Jumlah Heading</h3>
        <table>
            <tr><th>Heading</th><th>Jumlah</th></tr>
            {% for heading, count in seo_result.headings.items() %}
            <tr><td>{{ heading }}</td><td>{{ count }}</td></tr>
            {% endfor %}
        </table>
        <h3>Gambar</h3>
        <table>
            <tr><th>Total Gambar</th><td>{{ seo_result.images_total }}</td></tr>
            <tr><th>Gambar dengan atribut alt</th><td>{{ seo_result.images_with_alt }}</td></tr>
            <tr><th>Gambar tanpa atribut alt</th><td>{{ seo_result.images_without_alt }}</td></tr>
        </table>
        {% if seo_result.keyword %}
        <p><strong>Kata kunci "{{ seo_result.keyword }}" muncul sebanyak:</strong> {{ seo_result.keyword_count }} kali di teks halaman.</p>
        {% endif %}
        <p class="note">Catatan: Alat ini memberikan gambaran dasar analisis SEO. Analisis mendalam seperti backlink, performa server, dan lain-lain membutuhkan alat dan API khusus.</p>
    </div>
    {% endif %}
</body>
</html>
'''

def fetch_page(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        load_time = time.time() - start_time
        return response.text, round(load_time, 2), None
    except requests.RequestException as e:
        return None, None, str(e)

def analyze_seo(html_content, keyword=None):
    soup = BeautifulSoup(html_content, 'html.parser')

    title = soup.title.string.strip() if soup.title and soup.title.string else 'Tidak ada title ditemukan'

    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag['content'].strip() if description_tag and 'content' in description_tag.attrs else 'Tidak ada meta description ditemukan'

    headings = {}
    for i in range(1, 7):
        headings[f'h{i}'] = len(soup.find_all(f'h{i}'))

    images = soup.find_all('img')
    images_with_alt = sum(1 for img in images if img.has_attr('alt') and img['alt'].strip())
    images_without_alt = len(images) - images_with_alt

    keyword_count = 0
    if keyword:
        text = soup.get_text().lower()
        keyword_count = text.count(keyword.lower())

    class SEOResult:
        pass

    seo_result = SEOResult()
    seo_result.title = title
    seo_result.meta_description = description
    seo_result.headings = headings
    seo_result.images_total = len(images)
    seo_result.images_with_alt = images_with_alt
    seo_result.images_without_alt = images_without_alt
    seo_result.keyword = keyword if keyword else ''
    seo_result.keyword_count = keyword_count

    return seo_result

@app.route('/', methods=['GET', 'POST'])
def home():
    seo_result = None
    load_time = None
    error = None
    url = ''
    keyword = ''

    if request.method == 'POST':
        url = request.form.get('url','').strip()
        keyword = request.form.get('keyword','').strip()

        if not url:
            error = "URL wajib diisi."
        else:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            html_content, load_time, error_fetch = fetch_page(url)
            if error_fetch:
                error = f"Gagal mengambil halaman: {error_fetch}"
            else:
                seo_result = analyze_seo(html_content, keyword)

    return render_template_string(HTML_TEMPLATE, seo_result=seo_result, load_time=load_time, error=error, url=url, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)


