import requests
import re
from bs4 import BeautifulSoup
from .common import get_dm_m3u8

headers = {"User-Agent": "Mozilla/5.0"}


def extract_yunshanid(url):
    try:
        print("🔍 Yunshan URL:", url)

        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # 🔥 check ALL iframes
        iframes = soup.find_all("iframe")

        for iframe in iframes:
            src = iframe.get("src", "")

            if "dailymotion" in src:
                print("➡️ Found iframe:", src)

                match = re.search(r'video=([a-zA-Z0-9]+)', src)
                if match:
                    vid = match.group(1)

                    dm = f"https://www.dailymotion.com/video/{vid}"
                    m3u8 = get_dm_m3u8(dm)

                    print("✅ DM:", dm)
                    print("✅ M3U8:", m3u8)

                    return dm, m3u8

        print("❌ No DM found")
        return None, None

    except Exception as e:
        print("Yunshan error:", e)
        return None, None
