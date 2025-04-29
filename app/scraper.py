import json
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# === Selenium 設定 ===
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--lang=zh-TW")
driver = webdriver.Chrome(options=options)

driver.get("https://www.facebook.com/")
with open("cookie.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)
for cookie in cookies:
    driver.add_cookie(cookie)

driver.get("https://www.facebook.com/MissionImpossibleAU/")
time.sleep(2)

output_file = "facebook_posts2.csv"
if os.path.exists(output_file):
    os.remove(output_file)

posts_data = []
post_count = 0
max_posts = 35
start_time = time.time()
max_duration = 300  # 秒


# === 初始滑動避開封面區 ===
initial_scroll = driver.execute_script("return window.innerHeight * 0.3")
driver.execute_script(f"window.scrollBy(0, {initial_scroll});")
time.sleep(1.5)

while post_count < max_posts:
    if time.time() - start_time > max_duration:
        print("⏱ 超過90秒，提前結束")
        break

    posinset = post_count + 1
    post_xpath = f'//div[@aria-posinset="{posinset}"]'

    scroll_start = driver.execute_script("return window.scrollY")
    screen_height = driver.execute_script("return window.innerHeight")
    complete = False
    scroll_attempts = 0

    while not complete:
        try:
            post = driver.find_element(By.XPATH, post_xpath)
            if not post.is_displayed():
                raise Exception("not visible")
        except:
            driver.execute_script("window.scrollBy(0, 30);")
            time.sleep(0.1)
            scroll_attempts += 1
            if driver.execute_script("return window.scrollY") - scroll_start > screen_height+300:
                print(f"❌ aria-posinset={posinset} 超過一畫面高度仍無法定位，跳過")
                break
            continue

        # 嘗試抓資料（每滑一次就抓一次）
        content_elements = post.find_elements(By.XPATH, './/div[@dir="auto" and @style="text-align: start;"]')
        like_elements = post.find_elements(By.XPATH, './/span[@class="x1e558r4"]')
        comment_elements = post.find_elements(By.XPATH, './/span[@class="html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs xkrqix3 x1sur9pj"]')

        content_text = "\n".join([e.text.strip() for e in content_elements if e.text.strip()])
        like_count = like_elements[0].text.strip() if like_elements else ""
        comment_count = comment_elements[0].text.strip() if comment_elements else ""

        if content_text and like_count and comment_count:
            # ==== 擷取影片連結 ====
            video_link = ""
            video_candidates = post.find_elements(By.XPATH,
                './/div[contains(@class, "html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x6ikm8r x10wlt62")]//div[contains(@class, "x1s85apg")]/a')
            for a in video_candidates:
                href = a.get_attribute("href")
                if href:
                    video_link = href
                    break

            # ==== 擷取圖片連結 ====
            image_link = ""
            image_candidates = post.find_elements(By.XPATH,
                './/div[contains(@class, "html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x6ikm8r x10wlt62")]//div[@href]')
            for div in image_candidates:
                href = div.get_attribute("href")
                if href:
                    image_link = href
                    break

            posts_data.append({
                "Content": content_text,
                "LikeCount": like_count,
                "CommentCount": comment_count,
                "VideoLink": video_link,
                "ImageLink": image_link
            })
            print(f"✅ 成功抓取 aria-posinset={posinset}")
            complete = True
            break
        else:
            driver.execute_script("window.scrollBy(0, 50);")
            time.sleep(0.1)
            scroll_attempts += 1
            if driver.execute_script("return window.scrollY") - scroll_start > screen_height+300:
                print(f"❌ aria-posinset={posinset} 超過一畫面滑動仍資料不全，跳過")
                break

    post_count += 1

# 儲存
df = pd.DataFrame(posts_data)
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("🎉 抓取完成，共抓到", len(posts_data), "篇")
driver.quit()