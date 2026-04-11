import asyncio
import os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from scraper.sites import scrape_site

from extractors.animexin import extract_animexin
from extractors.lucifer import extract_lucifer
from extractors.yunshanid import extract_yunshanid
from extractors.myanime import extract_myanime


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


# ✅ ALL SITES BACK
SITE_STATUS = {
    "animexin": True,
    "luci": True,
    "yunshan": True,
    "myanime": True,
}

SITES = {
    "animexin": "https://animexin.dev",
    "luci": "https://luciferdonghua.in",
    "yunshan": "https://yunshanid.site",
    "myanime": "https://myanime.live",
}

posted = set()


# ===== ROUTER =====
def extract_video(site, url):
    if site == "animexin":
        return extract_animexin(url)

    elif site == "luci":
        return extract_lucifer(url)

    elif site == "yunshan":
        return extract_yunshanid(url)

    elif site == "myanime":
        return extract_myanime(url)

    return None, None


# ===== COMMANDS =====

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /active site")

    site = context.args[0].lower()

    if site in SITE_STATUS:
        SITE_STATUS[site] = True
        await update.message.reply_text(f"✅ {site} Enabled")
    else:
        await update.message.reply_text("❌ Invalid site")


async def deactive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /deactive site")

    site = context.args[0].lower()

    if site in SITE_STATUS:
        SITE_STATUS[site] = False
        await update.message.reply_text(f"❌ {site} Disabled")
    else:
        await update.message.reply_text("❌ Invalid site")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Site Status:\n\n"
    for s, v in SITE_STATUS.items():
        msg += f"{s} → {'✅ ON' if v else '❌ OFF'}\n"
    await update.message.reply_text(msg)


# 🔥 NEW COMMAND: /upload site
async def upload_site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /upload animexin")

    site = context.args[0].lower()

    if site not in SITES:
        return await update.message.reply_text("❌ Invalid site")

    posts = scrape_site(SITES[site])

    await update.message.reply_text(f"🚀 Uploading latest from {site}...")

    for title, link, img in posts[:2]:
        await send_post(context.application, title, link, img, site)


# 🔥 NEW COMMAND: /update (force all sites)
async def update_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Updating all sites...")

    for site in SITES:
        if SITE_STATUS.get(site):
            posts = scrape_site(SITES[site])

            for title, link, img in posts[:2]:
                await send_post(context.application, title, link, img, site)


# ===== SEND POST =====
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


# ===== MAIN LOOP (FIXED DEACTIVE BUG) =====
async def main_loop(app):
    print("🔥 Scraper running...")

    while True:
        for site_name, site_url in SITES.items():

            # 🔥 HARD CHECK (fix luci still posting bug)
            if SITE_STATUS.get(site_name) is not True:
                continue

            posts = scrape_site(site_url)

            for title, link, img in posts:

                if link in posted:
                    continue

                posted.add(link)

                print(f"🆕 [{site_name}] {title}")
                await send_post(app, title, link, img, site_name)

        await asyncio.sleep(120)


# ===== START =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("active", active))
    app.add_handler(CommandHandler("deactive", deactive))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("update", update_all))
    app.add_handler(CommandHandler("upload", upload_site))

    async def start_bg(app):
        asyncio.create_task(main_loop(app))

    app.post_init = start_bg

    print("🚀 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
