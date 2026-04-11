from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def extract_yunshanid_home():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get("https://yunshanid.site/")
    time.sleep(5)

    posts = []

    cards = driver.find_elements(By.CSS_SELECTOR, "div.group.relative")

    for card in cards[:10]:
        try:
            title = card.find_element(By.CSS_SELECTOR, "div.text-[11px]").text
            img = card.find_element(By.TAG_NAME, "img").get_attribute("src")

            # 🔥 CLICK TO OPEN (SPA navigation)
            card.click()
            time.sleep(3)

            url = driver.current_url

            posts.append((title, url, img))

            driver.back()
            time.sleep(2)

        except:
            continue

    driver.quit()
    return posts


def extract_yunshanid(url):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import time

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)

    dm = None
    m3u8 = None

    try:
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        src = iframe.get_attribute("src")

        if "dailymotion" in src:
            vid = src.split("video=")[-1].split("&")[0]
            dm = f"https://www.dailymotion.com/video/{vid}"

            # 🔥 YOUR WORKING M3U8 LOGIC
            from extractors.common import get_dm_m3u8
            m3u8 = get_dm_m3u8(dm)

    except:
        pass

    driver.quit()
    return dm, m3u8
