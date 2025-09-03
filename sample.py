import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------
# 🧠 Setup Selenium
# -------------------------------
options = Options()
# options.add_argument("--headless=new")  # Uncomment if needed
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.guvi.in/courses/?current_tab=paidcourse")
time.sleep(6)

# -------------------------------
# 📁 CSV File Setup
# -------------------------------
csv_file = "guvi_paid_courses.csv"
if not os.path.exists(csv_file):
    pd.DataFrame(columns=['Title', 'Link', 'Duration', 'Language', 'Price (Current)', 'Price (Original)']).to_csv(csv_file, index=False, encoding='utf-8-sig')

# -------------------------------
# 🔁 Extract + Append Function
# -------------------------------
total_courses = 0

def extract_courses():
    global total_courses
    courses = driver.find_elements(By.XPATH, '//a[contains(@class,"progressCard")]')
    print(f"📦 Found {len(courses)} course cards on screen...")

    data = []

    for course in courses:
        try:
            link = course.get_attribute("href")
            title = course.find_element(By.CLASS_NAME, "progress-title").text.strip()
        except:
            title = link = "N/A"

        try:
            duration = course.find_element(By.XPATH, './/svg[contains(@class, "lucide-clock3")]/following-sibling::span').text.strip()
        except:
            duration = "N/A"

        try:
            language = course.find_element(By.XPATH, './/svg[contains(@class, "lucide-globe")]/following-sibling::span').text.strip()
        except:
            language = "N/A"

        try:
            price_current = course.find_element(By.XPATH, './/span[contains(@class,"text-primary")]').text.strip()
            price_original = course.find_element(By.XPATH, './/del').text.strip()
        except:
            price_current = price_original = "N/A"

        data.append({
            "Title": title,
            "Link": link,
            "Duration": duration,
            "Language": language,
            "Price (Current)": price_current,
            "Price (Original)": price_original
        })

    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        existing_links = set(existing_df["Link"].dropna())
        data = [d for d in data if d["Link"] not in existing_links]

    if data:
        df = pd.DataFrame(data)
        df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False, encoding='utf-8-sig')
        print(f"💾 Saved {len(df)} new courses")
        total_courses += len(df)
    else:
        print("⚠️ No new courses found in this round.")

# -------------------------------
# 🔁 Scroll + View More Loop
# -------------------------------
while True:
    # Slow scroll to bottom
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
        time.sleep(1.5)

    extract_courses()

    try:
        view_more = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "View More")]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_more)
        time.sleep(2)
        try:
            view_more.click()
        except ElementClickInterceptedException:
            print("⚠️ Click intercepted, retrying after scroll adjustment...")
            driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(2)
            view_more.click()
        print("🔁 Clicked View More...\n")
        time.sleep(5)
    except NoSuchElementException:
        print("✅ No more 'View More' button.")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        break

# -------------------------------
# 🔚 Close Driver
# -------------------------------
driver.quit()
print(f"\n🎉 Done! Total new courses added: {total_courses}")
