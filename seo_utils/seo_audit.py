import requests
from bs4 import BeautifulSoup

def audit_seo(url):
    results = {
        "title": "",
        "meta_description": "",
        "h1_count": 0,
        "images_without_alt": 0,
        "internal_links": 0,
        "external_links": 0,
        "canonical_tag": "",
    }

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Title tag
        title_tag = soup.title.string if soup.title else ""
        results["title"] = title_tag.strip() if title_tag else ""

        # Meta description
        description = soup.find("meta", attrs={"name": "description"})
        results["meta_description"] = description["content"].strip() if description and "content" in description.attrs else ""

        # H1 tags
        results["h1_count"] = len(soup.find_all("h1"))

        # Images without alt
        images = soup.find_all("img")
        results["images_without_alt"] = sum(1 for img in images if not img.get("alt"))

        # Internal and external links
        links = soup.find_all("a", href=True)
        internal = 0
        external = 0
        for link in links:
            href = link["href"]
            if href.startswith("http") and not url in href:
                external += 1
            else:
                internal += 1
        results["internal_links"] = internal
        results["external_links"] = external

        # Canonical tag
        canonical = soup.find("link", rel="canonical")
        results["canonical_tag"] = canonical["href"] if canonical and "href" in canonical.attrs else ""

        return results

    except Exception as e:
        return {"error": str(e)}
