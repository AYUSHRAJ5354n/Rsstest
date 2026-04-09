import asyncio
import os

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

from scraper.sites import scrape_site, SITES
from extractors.animexin import extract_animexin
from extractors.lucifer import extract_lucifer

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(BOT_TOKEN)
posted = set()


# ===== ROUTER =====
def extract_video(url):
    if "animexin" in url:
        return extract_animexin(url)

    if "luciferdonghua" in url:
        return extract_lucifer(url)

    return None, None


def format_text(title, link):
    return f"""📺 <b>{title}</b>

🔗 <a href="{link}">Source</a>
"""


async def send_post(title, link, img):
    dm, m3u8 = await asyncio.to_thread(extract_video, link)

    buttons = []

    if dm:
        buttons.append([InlineKeyboardButton("▶️ Watch", url=dm)])

    if m3u8:
        buttons.append([InlineKeyboardButton("📡 Stream", url=m3u8)])

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    text = format_text(title, link)

    try:
        if img:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )

        await asyncio.sleep(4)

    except Exception as e:
        print("Send Error:", e)


async def main():
    print("🔥 CLEAN BOT RUNNING")

    while True:
        for site in SITES:
            posts = scrape_site(site)

            for title, link, img in posts:
                if link in posted:
                    continue

                posted.add(link)

                print("🆕", title)
                await send_post(title, link, img)

        await asyncio.sleep(180)


if __name__ == "__main__":
    asyncio.run(main())
