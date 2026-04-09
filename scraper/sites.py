import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

SITES = [
    "https://animexin.dev",
    "https://luciferdonghua.in"
]

def scrape_site(site):
    try:
        r = requests.get(site, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        posts = []

        for a in soup.find_all("a", href=True):
            link = a["href"]

            if "episode" not in link.lower():
                continue

            title = a.get_text(strip=True)
            img = None

            img_tag = a.find("img")
            if img_tag:
                img = img_tag.get("src")

            posts.append((title, link, img))

        return posts[:5]

    except:
        return []
