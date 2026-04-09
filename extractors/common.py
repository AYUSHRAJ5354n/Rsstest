import requests
import re

def get_dm_m3u8(dm_url):
    try:
        vid = re.search(r'/video/([a-zA-Z0-9]+)', dm_url)
        if not vid:
            return None

        vid = vid.group(1)

        api = f"https://www.dailymotion.com/player/metadata/video/{vid}"
        data = requests.get(api).json()

        # BEST QUALITY
        qualities = data.get("qualities", {})

        for q in ["1080", "720", "480", "380"]:
            if q in qualities:
                return qualities[q][0]["url"]

        return None

    except Exception as e:
        print("M3U8 Error:", e)
        return None
