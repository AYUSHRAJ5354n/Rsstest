from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def extract_yunshan_video(url):
    driver = get_driver()
    driver.get(url)
    time.sleep(6)

    dm = None
    m3u8 = None

    try:
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        src = iframe.get_attribute("src")

        if "dailymotion" in src:
            vid = src.split("video=")[-1].split("&")[0]
            dm = f"https://www.dailymotion.com/video/{vid}"

            from extractors.common import get_dm_m3u8
            m3u8 = get_dm_m3u8(dm)

    except Exception as e:
        print("Yunshan error:", e)

    driver.quit()
    return dm, m3u8
