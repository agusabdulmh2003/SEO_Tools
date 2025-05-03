from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse, urljoin

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
        .section-title { border-bottom: 2px solid #2980b9; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 0.8em; color: #2980b9; }
        ul.warnings { background: #ffe6e6; color: #a94442; border: 1px solid #a94442; padding: 1em; border-radius: 5px; }
        ul.warnings li { margin-bottom: 0.5em; }
        ul.recommendations { background: #e6f7ff; color: #31708f; border: 1px solid #31708f; padding: 1em; border-radius: 5px; }
        ul.recommendations li { margin-bottom: 0.5em; }
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
            <tr><th>Bahasa Halaman</th><td>{{ seo_result.language }}</td></tr>
            <tr><th>URL Canonical</th><td>{{ canonical_tag }}</td></tr>
            <tr><th>HTTPS digunakan</th><td>{{ https_used }}</td></tr>
            <tr><th>Panjang URL</th><td>{{ url_length }} karakter</td></tr>
        </table>

        <h3 class="section-title">Jumlah Heading</h3>
        <table>
            <tr><th>Heading</th><th>Jumlah</th></tr>
            {% for heading, count in seo_result.headings.items() %}
            <tr><td>{{ heading }}</td><td>{{ count }}</td></tr>
            {% endfor %}
        </table>
        <h3 class="section-title">Gambar</h3>
        <table>
            <tr><th>Total Gambar</th><td>{{ seo_result.images_total }}</td></tr>
            <tr><th>Gambar dengan atribut alt</th><td>{{ seo_result.images_with_alt }}</td></tr>
            <tr><th>Gambar tanpa atribut alt</th><td>{{ seo_result.images_without_alt }}</td></tr>
        </table>

        <h3 class="section-title">Link Halaman</h3>
        <table>
            <tr><th>Total Link</th><td>{{ seo_result.link_total }}</td></tr>
            <tr><th>Link Internal</th><td>{{ seo_result.link_internal }}</td></tr>
            <tr><th>Link Eksternal</th><td>{{ seo_result.link_external }}</td></tr>
        </table>

        {% if seo_result.keyword %}
        <h3 class="section-title">Analisis Kata Kunci</h3>
        <p><strong>Kata kunci "{{ seo_result.keyword }}" muncul sebanyak:</strong> {{ seo_result.keyword_count }} kali di teks halaman.</p>
        <p><strong>Kepadatan kata kunci:</strong> {{ keyword_density }}%</p>
        {% endif %}

        <h3 class="section-title">Pemeriksaan Sitemap dan Robots.txt</h3>
        <table>
            <tr><th>Sitemap (/sitemap.xml)</th><td>{{ sitemap_status }}</td></tr>
            <tr><th>Robots.txt</th><td>{{ robots_status }}</td></tr>
        </table>

        <h3 class="section-title">Penilaian Keterbacaan (Readability)</h3>
        <p>{{ readability_result }}</p>

        {% if warnings %}
        <h3 class="section-title">Peringatan SEO</h3>
        <ul class="warnings">
            {% for warn in warnings %}
            <li>{{ warn }}</li>
            {% endfor %}
        </ul>
        {% endif %}

        {% if recommendations %}
        <h3 class="section-title">Rekomendasi Perbaikan SEO</h3>
        <ul class="recommendations">
            {% for rec in recommendations %}
            <li>{{ rec }}</li>
            {% endfor %}
        </ul>
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

def analyze_seo(html_content, base_url, keyword=None):
    soup = BeautifulSoup(html_content, 'html.parser')

    title = soup.title.string.strip() if soup.title and soup.title.string else 'Tidak ada title ditemukan'

    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag['content'].strip() if description_tag and 'content' in description_tag.attrs else 'Tidak ada meta description ditemukan'

    # Language detection
    html_tag = soup.find('html')
    language = html_tag.get('lang', 'Tidak diketahui') if html_tag else 'Tidak diketahui'

    headings = {}
    for i in range(1, 7):
        headings[f'h{i}'] = len(soup.find_all(f'h{i}'))

    images = soup.find_all('img')
    images_with_alt = sum(1 for img in images if img.has_attr('alt') and img['alt'].strip())
    images_without_alt = len(images) - images_with_alt

    keyword_count = 0
    total_word_count = 0
    if keyword:
        text = soup.get_text().lower()
        keyword_count = text.count(keyword.lower())
        words = re.findall(r'\b\w+\b', text)
        total_word_count = len(words) if words else 0

    # Links analysis
    links = soup.find_all('a', href=True)
    link_total = len(links)
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.lower()
    link_internal = 0
    link_external = 0
    for link in links:
        href = link['href'].strip()
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        href_parsed = urlparse(urljoin(base_url, href))
        target_domain = href_parsed.netloc.lower()
        if target_domain == base_domain or target_domain == '':
            link_internal += 1
        else:
            link_external += 1

    # Canonical tag check
    canonical_tag = soup.find('link', rel='canonical')
    canonical_href = canonical_tag['href'].strip() if canonical_tag and 'href' in canonical_tag.attrs else 'Tidak ditemukan'

    class SEOResult:
        pass

    seo_result = SEOResult()
    seo_result.title = title
    seo_result.meta_description = description
    seo_result.language = language
    seo_result.headings = headings
    seo_result.images_total = len(images)
    seo_result.images_with_alt = images_with_alt
    seo_result.images_without_alt = images_without_alt
    seo_result.keyword = keyword if keyword else ''
    seo_result.keyword_count = keyword_count
    seo_result.total_word_count = total_word_count
    seo_result.link_total = link_total
    seo_result.link_internal = link_internal
    seo_result.link_external = link_external

    return seo_result, canonical_href

def check_url_exists(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False

def estimate_readability(text):
    # Simple readability: average sentence length (words per sentence)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return "Tidak cukup data untuk analisis keterbacaan."
    total_words = sum(len(re.findall(r'\b\w+\b', s)) for s in sentences)
    avg_sentence_len = total_words / len(sentences)
    if avg_sentence_len < 12:
        return f"Keterbacaan baik (Rata-rata panjang kalimat: {avg_sentence_len:.1f} kata)."
    elif avg_sentence_len < 20:
        return f"Keterbacaan sedang (Rata-rata panjang kalimat: {avg_sentence_len:.1f} kata)."
    else:
        return f"Keterbacaan rendah, kalimat cenderung panjang (Rata-rata panjang kalimat: {avg_sentence_len:.1f} kata)."

def generate_recommendations(seo_result, canonical_href, https_used, url_length, sitemap_status, robots_status, readability_result):
    recs = []

    if seo_result.title == 'Tidak ada title ditemukan':
        recs.append("Tambahkan tag <title> yang deskriptif dan relevan di halaman Anda.")
    if seo_result.meta_description == 'Tidak ada meta description ditemukan':
        recs.append("Tambahkan meta description yang menggambarkan isi halaman dengan jelas.")
    if seo_result.headings.get('h1', 0) == 0:
        recs.append("Tambahkan setidaknya satu tag heading <h1> pada halaman untuk judul utama.")
    if seo_result.images_without_alt > 0:
        recs.append(f"Tambahkan atribut alt pada gambar yang belum memiliki alt ({seo_result.images_without_alt} gambar).")
    if canonical_href == 'Tidak ditemukan':
        recs.append("Tambahkan tag canonical untuk menghindari duplikasi konten.")
    if https_used == 'Tidak':
        recs.append("Gunakan HTTPS untuk keamanan dan peningkatan peringkat SEO.")
    if url_length > 100:
        recs.append("Buat URL lebih singkat dan mudah dibaca, idealnya kurang dari 100 karakter.")
    if seo_result.link_external == 0:
        recs.append("Tambahkan link eksternal yang relevan untuk meningkatkan otoritas halaman.")
    if sitemap_status == 'Tidak ditemukan':
        recs.append("Buat file sitemap.xml untuk membantu mesin pencari mengindeks situs Anda.")
    if robots_status == 'Tidak ditemukan':
        recs.append("Tambahkan file robots.txt untuk mengatur akses mesin pencari ke situs Anda.")
    if 'rendah' in readability_result.lower():
        recs.append("Sederhanakan kalimat pada halaman untuk meningkatkan keterbacaan.")
    return recs

@app.route('/', methods=['GET', 'POST'])
def home():
    seo_result = None
    load_time = None
    error = None
    url = ''
    keyword = ''

    sitemap_status = 'Belum diperiksa'
    robots_status = 'Belum diperiksa'
    keyword_density = None
    readability_result = None
    canonical_href = 'Tidak ditemukan'
    https_used = 'Tidak diketahui'
    url_length = 0
    warnings = []
    recommendations = []

    if request.method == 'POST':
        url = request.form.get('url','').strip()
        keyword = request.form.get('keyword','').strip()

        if not url:
            error = "URL wajib diisi."
        else:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url

            https_used = 'Ya' if url.lower().startswith('https://') else 'Tidak'

            url_length = len(url)

            html_content, load_time, error_fetch = fetch_page(url)
            if error_fetch:
                error = f"Gagal mengambil halaman: {error_fetch}"
            else:
                seo_result, canonical_href = analyze_seo(html_content, url, keyword)
                if seo_result and seo_result.keyword and seo_result.total_word_count > 0:
                    keyword_density = round((seo_result.keyword_count / seo_result.total_word_count) * 100, 2)
                else:
                    keyword_density = 0.0

                # Check sitemap.xml
                sitemap_url = url.rstrip('/') + '/sitemap.xml'
                sitemap_status = "Ditemukan" if check_url_exists(sitemap_url) else "Tidak ditemukan"

                # Check robots.txt
                robots_url = url.rstrip('/') + '/robots.txt'
                robots_status = "Ditemukan" if check_url_exists(robots_url) else "Tidak ditemukan"

                # Readability estimate
                page_text = BeautifulSoup(html_content, 'html.parser').get_text(separator=' ')
                readability_result = estimate_readability(page_text)

                # SEO warnings
                if seo_result.title == 'Tidak ada title ditemukan':
                    warnings.append("Halaman tidak memiliki tag <title>.")
                if seo_result.meta_description == 'Tidak ada meta description ditemukan':
                    warnings.append("Halaman tidak memiliki meta description.")
                if seo_result.headings.get('h1', 0) == 0:
                    warnings.append("Halaman tidak memiliki tag heading <h1>.")
                if seo_result.images_without_alt > 0:
                    warnings.append(f"Ada {seo_result.images_without_alt} gambar tanpa atribut alt.")
                if canonical_href == 'Tidak ditemukan':
                    warnings.append("Tag canonical tidak ditemukan.")
                if url_length > 100:
                    warnings.append("Panjang URL lebih dari 100 karakter, sebaiknya dibuat lebih singkat untuk SEO.")
                if seo_result.link_external == 0:
                    warnings.append("Tidak ditemukan link eksternal pada halaman, link eksternal yang relevan dapat membantu SEO.")

                recommendations = generate_recommendations(seo_result, canonical_href, https_used, url_length, sitemap_status, robots_status, readability_result)

    return render_template_string(HTML_TEMPLATE,
                                  seo_result=seo_result,
                                  load_time=load_time,
                                  error=error,
                                  url=url,
                                  keyword=keyword,
                                  sitemap_status=sitemap_status,
                                  robots_status=robots_status,
                                  keyword_density=keyword_density,
                                  readability_result=readability_result,
                                  canonical_tag=canonical_href,
                                  https_used=https_used,
                                  url_length=url_length,
                                  warnings=warnings,
                                  recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)