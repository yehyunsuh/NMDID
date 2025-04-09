import os
import time
import argparse
import sys
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


def display_file_progress(filepath, refresh_rate=2):
    """
    Display file size growth during download and show total size + time taken in GB.
    """
    filename = os.path.basename(filepath)
    print(f"⏳ Downloading: {filename}")

    prev_size = -1
    start_time = time.time()

    while os.path.exists(filepath):
        try:
            size = os.path.getsize(filepath)
            if size != prev_size:
                elapsed = time.time() - start_time
                sys.stdout.write(
                    f"\r   Size: {size / 1024 / 1024 / 1024:.3f} GB | Elapsed: {elapsed:.1f} sec"
                )
                sys.stdout.flush()
                prev_size = size
        except Exception:
            pass
        time.sleep(refresh_rate)

    # Final size & duration
    final_size_gb = prev_size / 1024 / 1024 / 1024
    elapsed_time = time.time() - start_time
    sys.stdout.write(
        f"\r   ✅ Download complete! Total: {final_size_gb:.3f} GB in {elapsed_time:.1f} sec\n"
    )
    sys.stdout.flush()


def wait_for_downloads_to_finish(download_dir, check_interval=5):
    """
    Waits until no .part or .crdownload files remain in the download directory.
    Displays file size progress for each downloading file.
    """
    in_progress = set()
    print("⏳ Waiting for download to complete...")

    while True:
        files = os.listdir(download_dir)
        downloading = [f for f in files if f.endswith(".part") or f.endswith(".crdownload")]

        new_files = [f for f in downloading if f not in in_progress]
        for f in new_files:
            full_path = os.path.join(download_dir, f)
            in_progress.add(f)
            Thread(target=display_file_progress, args=(full_path,), daemon=True).start()

        if not downloading:
            time.sleep(2)    
            return

        time.sleep(check_interval)


def main(args):
    download_dir = os.path.abspath(args.download_dir)
    os.makedirs(download_dir, exist_ok=True)

    # === Firefox Profile Settings ===
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", download_dir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("browser.download.manager.showWhenStarting", False)

    # === Firefox Options ===
    options = Options()
    options.profile = profile
    options.binary_location = args.firefox_loc  # e.g. /snap/firefox/current/usr/lib/firefox/firefox
    options.headless = True  # ✅ Run in headless mode for SSH environments

    # === Launch Firefox ===
    driver = webdriver.Firefox(options=options)

    try:
        # === Login to NMDID ===
        driver.get("https://nmdid.unm.edu/login")
        time.sleep(3)
        driver.find_element(By.NAME, "email").send_keys(args.email)
        driver.find_element(By.NAME, "password").send_keys(args.password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)

        # === Go to cart and open download page ===
        driver.get("https://nmdid.unm.edu/carts/my-cart")
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, "Download Images").click()
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        # === Find and click download icons ===
        icons = driver.find_elements(By.CLASS_NAME, "glyphicon-download-alt")
        print(f"🔍 Found {len(icons)} files to download.")

        for i, icon in enumerate(icons[:args.max_files]):
            try:
                print(f"\n📥 Starting download {i + 1}/{args.max_files}")
                driver.execute_script("arguments[0].click();", icon)
                time.sleep(args.download_delay)  # allow it to start

                wait_for_downloads_to_finish(download_dir)
                print(f"✅ Finished download {i + 1}")

            except Exception as e:
                print(f"❌ Failed to download file {i + 1}: {e}")

        print("\n🎉 All downloads completed.")

    finally:
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download NMDID files sequentially using headless Firefox.")
    parser.add_argument('--email', required=True, help='NMDID login email')
    parser.add_argument('--password', required=True, help='NMDID login password')
    parser.add_argument('--download_dir', default='0_NMDID', help='Directory to save downloads')
    parser.add_argument('--download_delay', type=int, default=10, help='Delay to let download start (in seconds)')
    parser.add_argument('--firefox_loc', type=str, default='/usr/bin/firefox', help='Path to Firefox binary')
    parser.add_argument('--max_files', type=int, default=500, help='Max number of files to download')
    args = parser.parse_args()

    main(args)