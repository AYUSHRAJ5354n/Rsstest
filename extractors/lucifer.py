import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .common import get_dm_m3u8


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    return webdriver.Chrome(options=options)


def find_dm(html):
    # 🔥 1. iframe check
    iframe_match = re.search(r'<iframe[^>]+src="([^"]+dailymotion[^"]+)"', html)
    if iframe_match:
        src = iframe_match.group(1)

        vid = re.search(r'/video/([a-zA-Z0-9]+)', src)
        if vid:
            return vid.group(1)

    # 🔥 2. embed pattern
    embed_match = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', html)
    if embed_match:
        return embed_match.group(1)

    # 🔥 3. raw video pattern
    raw_match = re.search(r'dailymotion\.com/video/([a-zA-Z0-9]+)', html)
    if raw_match:
        return raw_match.group(1)

    return None


def extract_lucifer(url):
    driver = get_driver()

    try:
        # ✅ TRY ALL SERVERS
        for i in range(1, 5):
            test_url = url.rstrip("/") + f"/v/{i}/"
            print("Trying:", test_url)

            driver.get(test_url)
            time.sleep(5)

            html = driver.page_source

            vid = find_dm(html)

            if vid:
                dm = f"https://www.dailymotion.com/video/{vid}"
                m3u8 = get_dm_m3u8(dm)

                print("✅ FOUND:", dm)
                driver.quit()
                return dm, m3u8

        # ✅ FINAL FALLBACK → main page
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        vid = find_dm(html)

        if vid:
            dm = f"https://www.dailymotion.com/video/{vid}"
            m3u8 = get_dm_m3u8(dm)

            print("✅ FOUND MAIN:", dm)
            driver.quit()
            return dm, m3u8

        print("❌ No Dailymotion found")
        driver.quit()
        return None, None

    except Exception as e:
        print("Lucifer error:", e)
        driver.quit()
        return None, None
