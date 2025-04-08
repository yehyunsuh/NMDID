import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def main(args):
    # ===== USER-SPECIFIC CONFIGURATION =====
    EMAIL = args.email
    PASSWORD = args.password
    DOWNLOAD_DIR = args.download_dir
    CHROMEDRIVER_PATH = args.chromedriver
    DOWNLOAD_DELAY = args.download_delay

    # ===== SETUP CHROME OPTIONS =====
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    })
    chrome_options.add_argument("--start-maximized")

    # ===== START DRIVER =====
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # ===== TODO 1: VISIT LOGIN PAGE =====
    driver.get("https://nmdid.unm.edu/login")
    time.sleep(3)

    # ===== TODO 2: LOGIN =====
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)

    # ===== TODO 3: GO TO CART =====
    driver.get("https://nmdid.unm.edu/carts/my-cart")
    time.sleep(3)

    # ===== TODO 4: CLICK "DOWNLOAD IMAGES" =====
    download_button = driver.find_element(By.LINK_TEXT, "Download Images")
    download_button.click()
    time.sleep(5)

    # ===== TODO 5: SWITCH TO NEW TAB =====
    tabs = driver.window_handles
    driver.switch_to.window(tabs[-1])
    time.sleep(5)

    # ===== TODO 6: CLICK ALL DOWNLOAD ICONS =====
    download_icons = driver.find_elements(By.CLASS_NAME, "glyphicon-download-alt")
    print(f"Found {len(download_icons)} download buttons.")

    for i, icon in enumerate(download_icons[:1]):
        try:
            driver.execute_script("arguments[0].click();", icon)
            print(f"Clicked file {i+1}/{len(download_icons)}")
            time.sleep(DOWNLOAD_DELAY)
        except Exception as e:
            print(f"Error on file {i+1}: {e}")

    # ===== TODO 7: WAIT FOR DOWNLOADS TO FINISH =====
    print("Waiting for downloads to complete...")
    while any(fname.endswith(".crdownload") for fname in os.listdir(DOWNLOAD_DIR)):
        print("Downloading still in progress...")
        time.sleep(DOWNLOAD_DELAY/2)

    print("✅ All downloads completed!")
    driver.quit()  # Uncomment if you want to close the browser automatically


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unzip zip files')

    parser.add_argument('--email', type=str, help='user email', required=True, default='your@email.com')
    parser.add_argument('--password', type=str, help='user password', required=True, default='your_password')
    parser.add_argument('--download_dir', type=str, help='download directory', default='0_NMDID')
    parser.add_argument('--chromedriver', type=str, help='path to chromedriver', default='/usr/local/bin/chromedriver')
    parser.add_argument('--download_delay', type=int, help='delay between downloads in seconds', default=60)

    args = parser.parse_args()

    main(args)