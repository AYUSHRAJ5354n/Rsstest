import requests
import re
from bs4 import BeautifulSoup
from .common import extract_m3u8_from_dm

headers = {"User-Agent": "Mozilla/5.0"}

def extract_animexin(url):
    try:
        r = requests.get(url, headers=headers)
        html = r.text

        soup = BeautifulSoup(html, "html.parser")

        iframe = soup.find("iframe")

        if iframe:
            src = iframe.get("src")

            if "dailymotion" in src:
                vid = re.search(r'/video/([a-zA-Z0-9]+)', src)
                if vid:
                    dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                    m3u8 = extract_m3u8_from_dm(dm)
                    return dm, m3u8

        return None, None

    except Exception as e:
        print("Animexin error:", e)
        return None, None
