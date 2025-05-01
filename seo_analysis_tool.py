import requests
from bs4 import BeautifulSoup
import time

def fetch_page(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        load_time = time.time() - start_time
        response.raise_for_status()
        return response.text, load_time
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None, None

def analyze_seo(html_content, keyword=None):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Title tag
    title = soup.title.string.strip() if soup.title and soup.title.string else 'No title found'

    # Meta description
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag['content'].strip() if description_tag and 'content' in description_tag.attrs else 'No meta description found'

    # Headings count
    headings = {}
    for level in range(1,7):
        headings[f'h{level}'] = len(soup.find_all(f'h{level}'))

    # Images with alt attribute count
    images = soup.find_all('img')
    images_with_alt = sum(1 for img in images if img.has_attr('alt') and img['alt'].strip() != '')
    images_without_alt = len(images) - images_with_alt

    # Keyword occurrences in text content
    keyword_count = 0
    if keyword:
        text = soup.get_text().lower()
        keyword_count = text.count(keyword.lower())

    # Basic SEO summary
    seo_data = {
        'title': title,
        'meta_description': description,
        'headings': headings,
        'images_total': len(images),
        'images_with_alt': images_with_alt,
        'images_without_alt': images_without_alt,
        'keyword': keyword if keyword else '',
        'keyword_count': keyword_count,
    }

    return seo_data

def main():
    print("SEO Analysis Tool")
    url = input("Enter the URL to analyze: ").strip()
    if not url.startswith('http'):
        url = 'http://' + url
    keyword = input("Enter a keyword to check (optional): ").strip()

    print(f"\nFetching {url} ...")
    html_content, load_time = fetch_page(url)
    if html_content is None:
        print("Failed to retrieve page. Exiting.")
        return

    print(f"Page loaded in {load_time:.2f} seconds.")

    print("Analyzing SEO factors...")
    seo_result = analyze_seo(html_content, keyword)

    print("\n--- SEO Analysis Result ---")
    print(f"Title tag: {seo_result['title']}")
    print(f"Meta description: {seo_result['meta_description']}")
    print("Headings count:")
    for heading, count in seo_result['headings'].items():
        print(f"  {heading}: {count}")
    print(f"Total images: {seo_result['images_total']}")
    print(f"Images with alt attribute: {seo_result['images_with_alt']}")
    print(f"Images missing alt attribute: {seo_result['images_without_alt']}")
    if seo_result['keyword']:
        print(f"Keyword \"{seo_result['keyword']}\" occurrences in page text: {seo_result['keyword_count']}")

    print("\nNote: This tool provides basic SEO insights. Advanced metrics like backlinks and page speed require specialized APIs or tools.")

if __name__ == '__main__':
    main()
