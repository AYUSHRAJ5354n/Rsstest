import requests
import re
from bs4 import BeautifulSoup
from .common import get_dm_m3u8

headers = {"User-Agent": "Mozilla/5.0"}


def extract_myanime(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # 🔥 DIRECTLY FIND GEO PLAYER (NO IFRAME NEEDED)
        iframe = soup.find("iframe", src=re.compile("dailymotion"))

        if not iframe:
            return None, None

        src = iframe.get("src")

        print("➡️ Found player:", src)

        # 🔥 EXTRACT VIDEO ID
        match = re.search(r'video=([a-zA-Z0-9]+)', src)

        if not match:
            return None, None

        vid = match.group(1)

        # 🔥 CONVERT TO NORMAL DM LINK
        dm = f"https://www.dailymotion.com/video/{vid}"

        # 🔥 GET M3U8
        m3u8 = get_dm_m3u8(dm)

        print("✅ DM:", dm)
        print("✅ M3U8:", m3u8)

        return dm, m3u8

    except Exception as e:
        print("MyAnime error:", e)
        return None, None
