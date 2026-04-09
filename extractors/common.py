import re

def extract_m3u8_from_dm(url):
    if not url:
        return None

    # convert embed → manifest
    vid = re.search(r'/video/([a-zA-Z0-9]+)', url)
    if not vid:
        return None

    vid = vid.group(1)

    return f"https://www.dailymotion.com/cdn/manifest/video/{vid}.m3u8"
