import requests
import re
from bs4 import BeautifulSoup
from .common import get_dm_m3u8

headers = {"User-Agent": "Mozilla/5.0"}


def extract_yunshanid(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        iframe = soup.find("iframe", src=re.compile("dailymotion"))

        if not iframe:
            return None, None

        src = iframe.get("src")

        match = re.search(r'video=([a-zA-Z0-9]+)', src)
        if not match:
            return None, None

        vid = match.group(1)

        dm = f"https://www.dailymotion.com/video/{vid}"
        m3u8 = get_dm_m3u8(dm)

        return dm, m3u8

    except Exception as e:
        print("Yunshan error:", e)
        return None, None
