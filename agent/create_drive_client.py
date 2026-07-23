"""create_drive_client.py — Auto-create Drive/Photos OAuth client via Playwright"""
import os, json, time
from playwright.sync_api import sync_playwright

PROFILE_PATH = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Profile 11")
PROJECT = "starlit-respect-416516"
CLIENT_NAME = "Drive Photos Scanner"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client_secret_drive.json")

print("Launching Chrome with amd949609 profile...")
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        headless=False,
        args=["--window-size=1400,900", "--no-first-run"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    url = f"https://console.cloud.google.com/apis/credentials/oauthclient?project={PROJECT}"
    print(f"Navigating to {url}...")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)

    print(f"Current URL: {page.url}")
    page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "console_step1.png"))

    # Check if we got redirected to sign-in
    if "signin" in page.url.lower() or "accounts.google.com" in page.url.lower():
        print("Session expired - waiting for user to sign in...")
        input("Press Enter after signing in...")

    # Look for the Desktop app selection
    desktop_selectors = [
        "text=Desktop app",
        "text=Desktop App",
        'md-radio-button[value="desktop"]',
        "//span[contains(text(),'Desktop app')]",
        '[role="radio"]:has-text("Desktop")',
    ]
    for sel in desktop_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=3000):
                el.click()
                print(f"Selected Desktop app via: {sel}")
                time.sleep(1)
                break
        except:
            continue

    # Fill in the name
    name_inputs = page.locator('input[type="text"]')
    for i in range(name_inputs.count()):
        try:
            el = name_inputs.nth(i)
            if el.is_visible(timeout=2000):
                el.fill(CLIENT_NAME)
                print(f"Filled name: {CLIENT_NAME}")
                time.sleep(1)
                break
        except:
            continue

    # Click Create
    create_btn = page.locator("text=Create").first
    if create_btn.is_visible(timeout=3000):
        create_btn.click()
        print("Clicked Create")
        time.sleep(5)

    page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "console_step2.png"))

    # Look for Download JSON
    download_btn = page.locator("text=Download JSON").first
    if download_btn.is_visible(timeout=5000):
        with page.expect_download() as download_info:
            download_btn.click()
        download = download_info.value
        download.save_as(OUTPUT_FILE)
        print(f"Downloaded to {OUTPUT_FILE}")
    else:
        print("No Download JSON button found. Trying alternate approach...")
        # Maybe it's a dialog - look for the download link
        download_link = page.locator("a:has-text('Download')").first
        if download_link.is_visible(timeout=3000):
            with page.expect_download() as download_info:
                download_link.click()
            download = download_info.value
            download.save_as(OUTPUT_FILE)
            print(f"Downloaded to {OUTPUT_FILE}")
        else:
            print("Could not find download button. Check screenshots.")
            input("Press Enter after saving manually...")

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        print(f"SUCCESS! Client ID: {data.get('installed', {}).get('client_id', 'unknown')}")

    time.sleep(3)
    ctx.close()
