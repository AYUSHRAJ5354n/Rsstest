import re
import aiohttp
import asyncio

METADATA_URL = (
    "https://www.dailymotion.com/player/metadata/video/{vid}"
    "?embedder=https%3A%2F%2Fwww.dailymotion.com&locale=en_US"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.dailymotion.com/",
}


def extract_video_id(url):
    if not url:
        return None

    # normal
    match = re.search(r'/video/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)

    # short
    match = re.search(r'dai\.ly/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)

    return None


def get_dm_m3u8(url):
    vid = extract_video_id(url)
    if not vid:
        return None

    return asyncio.run(fetch_m3u8(vid))


async def fetch_m3u8(video_id):
    api_url = METADATA_URL.format(vid=video_id)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=HEADERS) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json(content_type=None)

                qualities = data.get("qualities", {})
                auto = qualities.get("auto", [])

                for item in auto:
                    if item.get("type") == "application/x-mpegURL":
                        return item.get("url")

    except Exception as e:
        print("M3U8 error:", e)

    return None
