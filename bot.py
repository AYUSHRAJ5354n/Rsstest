import asyncio
import os
import re
import requests
from bs4 import BeautifulSoup

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(BOT_TOKEN)
posted = set()

headers = {"User-Agent": "Mozilla/5.0"}


# ================= DRIVER =================
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    return webdriver.Chrome(options=options)


# ================= METHOD 1: HTML =================
def extract_html(html):
    dm = None
    m3u8 = None

    dm_match = re.search(r'dailymotion.*?/video/([a-zA-Z0-9]+)', html)
    if dm_match:
        dm = f"https://www.dailymotion.com/video/{dm_match.group(1)}"

    m3u8_match = re.search(r'https://[^"]+\.m3u8[^"]*', html)
    if m3u8_match:
        m3u8 = m3u8_match.group(0)

    return dm, m3u8


# ================= METHOD 2: REQUEST =================
def extract_requests(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return extract_html(r.text)
    except:
        return None, None


# ================= METHOD 3: API DETECT =================
def extract_api(html):
    dm = None

    # common JSON player
    match = re.search(r'"videoId":"(.*?)"', html)
    if match:
        dm = f"https://www.dailymotion.com/video/{match.group(1)}"

    return dm, None


# ================= METHOD 4: SELENIUM =================
def extract_selenium(url):
    driver = get_driver()
    driver.get(url)

    dm = None
    m3u8 = None

    try:
        import time
        time.sleep(6)

        html = driver.page_source

        dm, m3u8 = extract_html(html)

        # try iframe click
        if not dm:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and "dailymotion" in src:
                    vid = re.search(r'/video/([a-zA-Z0-9]+)', src)
                    if vid:
                        dm = f"https://www.dailymotion.com/video/{vid.group(1)}"
                        break

    except Exception as e:
        print("Selenium error:", e)

    driver.quit()
    return dm, m3u8


# ================= MASTER EXTRACT =================
def extract_video(url):
    # 1️⃣ Fast method
    dm, m3u8 = extract_requests(url)
    if dm or m3u8:
        return dm, m3u8

    # 2️⃣ API sniff
    try:
        r = requests.get(url, headers=headers)
        dm2, _ = extract_api(r.text)
        if dm2:
            return dm2, None
    except:
        pass

    # 3️⃣ Selenium fallback
    return extract_selenium(url)


# ================= GENERIC SCRAPER =================
def scrape_site(base_url):
    try:
        r = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        posts = []

        for a in soup.find_all("a", href=True):
            link = a["href"]

            if "episode" not in link.lower():
                continue

            title = a.get_text(strip=True)
            if not title:
                continue

            img = None
            img_tag = a.find("img")
            if img_tag:
                img = img_tag.get("src")

            posts.append((title, link, img))

        return posts[:5]

    except Exception as e:
        print(f"Error scraping {base_url}:", e)
        return []


# ================= SITES =================
SITES = [
    "https://animexin.dev",
    "https://luciferdonghua.in",
    "https://animecube.live",
    "https://donghuafun.com",
    "https://anichin.care",
    "https://donghuazone.com",
    "https://donghuastream.org",
    "https://animekhor.org",
    "https://yunshanid.site",
    "https://dongstream.com",
    "https://topchineseanime.online",
    "https://animedonghua.io",
    "https://myanime.live"
]


# ================= FORMAT =================
def format_text(title, link):
    ep = re.search(r'(\d+)', title)
    ep_num = ep.group(1) if ep else "?"

    return f"""📺 <b>{title}</b>

Ep {ep_num}

🔗 <a href="{link}">Watch</a>
"""


# ================= SEND =================
async def send_post(title, link, img):
    dm, m3u8 = await asyncio.to_thread(extract_video, link)

    text = format_text(title, link)

    buttons = []

    if dm:
        buttons.append([InlineKeyboardButton("▶️ Watch", url=dm)])

    if m3u8:
        buttons.append([InlineKeyboardButton("📡 Stream", url=m3u8)])

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

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


# ================= MAIN =================
async def main():
    print("🔥 ULTIMATE BOT RUNNING")

    while True:
        print("🔄 Checking all sites...")

        for site in SITES:
            print("🌐", site)

            posts = scrape_site(site)

            for title, link, img in posts:
                if link in posted:
                    continue

                posted.add(link)
                print("🆕", title)

                await send_post(title, link, img)

        await asyncio.sleep(180)


# ================= START =================
if __name__ == "__main__":
    asyncio.run(main())
