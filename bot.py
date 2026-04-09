import asyncio
import os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from scraper.sites import scrape_site

from extractors.animexin import extract_animexin
from extractors.lucifer import extract_lucifer
from extractors.myanime import extract_myanime
from extractors.yunshanid import extract_yunshanid


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


SITE_STATUS = {
    "animexin": True,
    "luci": False,
    "myanime": True,
    "yunshan": True,
}

SITES = {
    "animexin": "https://animexin.dev",
    "luci": "https://luciferdonghua.in",
    "myanime": "https://myanime.live",
    "yunshan": "https://yunshanid.site",
}

posted = set()


def extract_video(site, url):
    if site == "animexin":
        return extract_animexin(url)

    elif site == "luci":
        return extract_lucifer(url)

    elif site == "myanime":
        return extract_myanime(url)

    elif site == "yunshan":
        return extract_yunshanid(url)

    return None, None


async def active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    site = context.args[0].lower()

    if site in SITE_STATUS:
        SITE_STATUS[site] = True
        await update.message.reply_text(f"✅ {site} Enabled")


async def deactive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    site = context.args[0].lower()

    if site in SITE_STATUS:
        SITE_STATUS[site] = False
        await update.message.reply_text(f"❌ {site} Disabled")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Site Status:\n\n"

    for s, v in SITE_STATUS.items():
        msg += f"{s} → {'✅ ON' if v else '❌ OFF'}\n"

    await update.message.reply_text(msg)


async def send_post(app, title, link, img, site):
    dm, m3u8 = await asyncio.to_thread(extract_video, site, link)

    buttons = []

    if dm:
        buttons.append([InlineKeyboardButton("▶️ Dailymotion", url=dm)])

    if m3u8:
        buttons.append([InlineKeyboardButton("📡 M3U8", url=m3u8)])

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    text = f"""📺 {title}

🌐 Source: {link}
"""

    try:
        if img:
            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption=text,
                reply_markup=keyboard
            )
        else:
            await app.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                reply_markup=keyboard
            )

        await asyncio.sleep(5)

    except Exception as e:
        print("Send Error:", e)


async def main_loop(app):
    print("🔥 Scraper running...")

    while True:
        for site_name, site_url in SITES.items():

            if not SITE_STATUS.get(site_name, False):
                continue

            posts = scrape_site(site_url)

            for title, link, img in posts:
                if link in posted:
                    continue

                posted.add(link)

                print(f"🆕 [{site_name}] {title}")
                await send_post(app, title, link, img, site_name)

        await asyncio.sleep(180)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("active", active))
    app.add_handler(CommandHandler("deactive", deactive))
    app.add_handler(CommandHandler("status", status))

    async def start_background(app):
        asyncio.create_task(main_loop(app))

    app.post_init = start_background

    print("🚀 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
