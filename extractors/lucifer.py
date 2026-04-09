import requests
import re
from bs4 import BeautifulSoup
from .common import get_dm_m3u8

headers = {"User-Agent": "Mozilla/5.0"}

def extract_lucifer(url):
    try:
        r = requests.get(url, headers=headers)
        html = r.text

        soup = BeautifulSoup(html, "html.parser")

        # 1. Try iframe (rare case)
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src")
            if src and "dailymotion" in src:
                vid = re.search(r'/video/([a-zA-Z0-9]+)', src)
                if vid:
                    dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                    m3u8 = get_dm_m3u8(dm)
                    return dm, m3u8

        # 2. Search in scripts (MAIN METHOD)
        scripts = soup.find_all("script")

        for script in scripts:
            if script.string:
                matches = re.findall(r'https?://www\.dailymotion\.com/embed/video/[a-zA-Z0-9]+', script.string)

                if matches:
                    embed = matches[0]

                    vid = re.search(r'/video/([a-zA-Z0-9]+)', embed)
                    if vid:
                        dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                        m3u8 = get_dm_m3u8(dm)
                        return dm, m3u8

        return None, None

    except Exception as e:
        print("Lucifer error:", e)
        return None, None
