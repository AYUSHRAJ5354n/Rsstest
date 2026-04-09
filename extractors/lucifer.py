import requests
from bs4 import BeautifulSoup
import re
from .common import extract_m3u8_from_dm

headers = {"User-Agent": "Mozilla/5.0"}

def extract_lucifer(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        iframes = soup.find_all("iframe")

        for iframe in iframes:
            src = iframe.get("src")

            if not src:
                continue

            if "dailymotion" in src:
                vid = re.search(r'/video/([a-zA-Z0-9]+)', src)
                if vid:
                    dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                    m3u8 = extract_m3u8_from_dm(dm)
                    return dm, m3u8

        return None, None

    except Exception as e:
        print("Lucifer error:", e)
        return None, None
