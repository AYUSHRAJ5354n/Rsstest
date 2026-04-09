import asyncio
import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.environ.get("PORT", 8000))

bot = Bot(BOT_TOKEN)
posted = set()

headers = {"User-Agent": "Mozilla/5.0"}

# ================= HEALTH SERVER =================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"🌐 Health server running on port {PORT}")
    server.serve_forever()

# ================= DRIVER =================
def get_driver():
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")

        options.binary_location = "/usr/bin/chromium"

        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print("❌ Selenium failed:", e)
        return None

# ================= EXTRACT =================
def extract_video(url):
    driver = get_driver()

    if not driver:
        return None

    driver.get(url)
    video_url = None

    try:
        import time
        time.sleep(5)

        # 🔥 find iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and "dailymotion" in src:
                video_url = src
                break

        # 🔥 fallback → search page
        if not video_url:
            html = driver.page_source

            import re
            match = re.search(r'https://[^"]*dailymotion[^"]+', html)
            if match:
                video_url = match.group(0)

    except Exception as e:
        print("Extract error:", e)

    driver.quit()
    return video_url

# ================= SCRAPER =================
def get_posts():
    url = "https://luciferdonghua.in/"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for a in soup.find_all("a"):
        link = a.get("href")

        if not link or "episode" not in link:
            continue

        title = a.text.strip()

        img = None
        img_tag = a.find("img")
        if img_tag:
            img = img_tag.get("src")

        posts.append((title, link, img))

    return posts[:5]

# ================= SEND =================
async def send_post(title, link, img):
    video = await asyncio.to_thread(extract_video, link)

    text = f"""
📺 <b>{title}</b>

🔗 <a href="{link}">Watch</a>
"""

    if video:
        text += f"\n🎬 <a href='{video}'>Stream</a>"

    try:
        if img:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption=text,
                parse_mode=ParseMode.HTML
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML
            )

        await asyncio.sleep(3)

    except Exception as e:
        print("Send Error:", e)

# ================= MAIN =================
async def main():
    print("🔥 Bot Running...")

    while True:
        print("🔄 Checking Lucifer...")

        posts = get_posts()

        for title, link, img in posts:
            if link in posted:
                continue

            posted.add(link)
            print("🆕", title)

            await send_post(title, link, img)

        await asyncio.sleep(60)

# ================= START =================
if __name__ == "__main__":
    # start health server (for koyeb)
    threading.Thread(target=run_server, daemon=True).start()

    asyncio.run(main())
