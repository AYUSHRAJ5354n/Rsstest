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


def extract_lucifer(url):
    driver = get_driver()

    try:
        # 🔥 TRY /v/1/ to /v/4/
        for i in range(1, 5):
            test_url = url.rstrip("/") + f"/v/{i}/"
            print("Trying:", test_url)

            driver.get(test_url)
            time.sleep(5)

            html = driver.page_source

            match = re.search(r'dailymotion.*?/video/([a-zA-Z0-9]+)', html)

            if match:
                vid = match.group(1)
                dm = f"https://www.dailymotion.com/video/{vid}"
                m3u8 = get_dm_m3u8(dm)

                driver.quit()
                return dm, m3u8

        # fallback main page
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        match = re.search(r'dailymotion.*?/video/([a-zA-Z0-9]+)', html)

        if match:
            vid = match.group(1)
            dm = f"https://www.dailymotion.com/video/{vid}"
            m3u8 = get_dm_m3u8(dm)

            driver.quit()
            return dm, m3u8

        driver.quit()
        return None, None

    except Exception as e:
        print("Lucifer error:", e)
        driver.quit()
        return None, None
