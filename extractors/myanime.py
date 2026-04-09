import requests
import re
from bs4 import BeautifulSoup
from .common import get_dm_m3u8

headers = {"User-Agent": "Mozilla/5.0"}


def extract_myanime(url):
    try:
        r = requests.get(url, headers=headers)
        html = r.text

        soup = BeautifulSoup(html, "html.parser")

        # 🔥 iframe
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src")

            if src and "dailymotion" in src:
                vid = re.search(r'/video/([a-zA-Z0-9]+)', src)
                if vid:
                    dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                    return dm, get_dm_m3u8(dm)

        # 🔥 script scan
        scripts = soup.find_all("script")

        for script in scripts:
            if script.string:
                match = re.search(r'dailymotion.*?/video/([a-zA-Z0-9]+)', script.string)

                if match:
                    dm = f"https://www.dailymotion.com/video/{match.group(1)}"
                    return dm, get_dm_m3u8(dm)

        # 🔥 fallback
        match = re.search(r'dailymotion.*?/video/([a-zA-Z0-9]+)', html)

        if match:
            dm = f"https://www.dailymotion.com/video/{match.group(1)}"
            return dm, get_dm_m3u8(dm)

        return None, None

    except Exception as e:
        print("MyAnime error:", e)
        return None, None
