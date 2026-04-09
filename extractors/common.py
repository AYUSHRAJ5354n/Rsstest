import re
import asyncio
import aiohttp

METADATA_URL = (
    "https://www.dailymotion.com/player/metadata/video/{vid}"
    "?embedder=https%3A%2F%2Fwww.dailymotion.com&locale=en_US"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.dailymotion.com/",
    "Accept": "application/json, text/plain, */*",
}

async def resolve_dm_async(video_id):
    url = METADATA_URL.format(vid=video_id)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            data = await resp.json(content_type=None)

            qualities = data.get("qualities", {})
            auto = qualities.get("auto", [])

            for item in auto:
                if item.get("type") == "application/x-mpegURL":
                    return item.get("url")

    return None


def get_dm_m3u8(dm_url):
    try:
        vid = re.search(r'/video/([a-zA-Z0-9]+)', dm_url)
        if not vid:
            return None

        vid = vid.group(1)

        return asyncio.run(resolve_dm_async(vid))

    except Exception as e:
        print("M3U8 Error:", e)
        return None
