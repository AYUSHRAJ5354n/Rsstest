import requests
import re
from bs4 import BeautifulSoup
from .common import get_dm_m3u8

headers = {"User-Agent": "Mozilla/5.0"}


def extract_myanime(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # 🔥 STEP 1: find iframe in main page
        iframe = soup.find("iframe")

        if not iframe:
            return None, None

        iframe_url = iframe.get("src")

        if not iframe_url:
            return None, None

        print("➡️ iframe:", iframe_url)

        # 🔥 STEP 2: open iframe page
        r2 = requests.get(iframe_url, headers=headers)
        html2 = r2.text

        # 🔥 STEP 3: find dailymotion inside iframe page
        match = re.search(r'dailymotion.*?/video/([a-zA-Z0-9]+)', html2)

        if match:
            vid = match.group(1)
            dm = f"https://www.dailymotion.com/video/{vid}"
            m3u8 = get_dm_m3u8(dm)

            print("✅ Found DM:", dm)
            return dm, m3u8

        # 🔥 STEP 4: fallback (sometimes nested iframe again)
        soup2 = BeautifulSoup(html2, "html.parser")

        for iframe2 in soup2.find_all("iframe"):
            src2 = iframe2.get("src")

            if src2 and "dailymotion" in src2:
                vid = re.search(r'/video/([a-zA-Z0-9]+)', src2)

                if vid:
                    dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                    m3u8 = get_dm_m3u8(dm)

                    print("✅ Found nested DM:", dm)
                    return dm, m3u8

        return None, None

    except Exception as e:
        print("MyAnime error:", e)
        return None, None
