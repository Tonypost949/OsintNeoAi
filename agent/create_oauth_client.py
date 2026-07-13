"""
create_oauth_client.py — Automate Google Cloud Console to create an OAuth client
==============================================================================
Launches Chrome with Profile 8 (txtdjdrop@gmail.com — Owner of project-743aab84-f9a5-4ec7-954)
and navigates to the OAuth client creation page.

Usage: python create_oauth_client.py
"""
import os, sys, json, time
from playwright.sync_api import sync_playwright

PROFILE_PATH = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Profile 8")
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
CLIENT_NAME = "Tasks Desktop Client"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "client_secret_tasks.json")

def main():
    print("[*] Launching Chrome with Profile 8 (txtdjdrop@gmail.com)...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--window-size=1280,900",
            ],
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        # Navigate to OAuth client creation page
        url = f"https://console.cloud.google.com/apis/credentials/oauthclient?project={PROJECT_ID}"
        print(f"[*] Navigating to {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait for page to load
        time.sleep(3)

        # Check if we're on the right page
        current_url = page.url
        print(f"[*] Current URL: {current_url}")

        # Take screenshot to see what's happening
        screenshot_path = os.path.join(OUTPUT_DIR, "console_screenshot.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"[*] Screenshot saved to {screenshot_path}")

        # Check if we need to select application type
        # The URL might redirect to a selection page
        if "oauthclient" in page.url:
            # Try to select "Desktop app" type
            selectors = [
                "text=Desktop app",
                "text=Desktop App",
                'input[value="desktop"]',
                "label:has-text('Desktop')",
                '[data-testid="application-type-desktop"]',
                "//span[contains(text(),'Desktop')]",
            ]
            for sel in selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=5000):
                        el.click()
                        print(f"[*] Selected 'Desktop app' via: {sel}")
                        time.sleep(1)
                        break
                except:
                    continue

            # Look for the name input and fill it
            name_selectors = [
                'input[aria-label*="name"]',
                'input[placeholder*="Name"]',
                'input[name*="name"]',
                "//input[@type='text']",
            ]
            for sel in name_selectors:
                try:
                    inputs = page.locator(sel)
                    count = inputs.count()
                    for i in range(count):
                        el = inputs.nth(i)
                        if el.is_visible(timeout=3000):
                            el.fill(CLIENT_NAME)
                            print(f"[*] Filled name: {CLIENT_NAME}")
                            time.sleep(1)
                            break
                    else:
                        continue
                    break
                except:
                    continue

            # Click Create button
            create_selectors = [
                "text=Create",
                "button:has-text('Create')",
                '[data-testid="create-button"]',
                "//span[contains(text(),'Create')]",
            ]
            for sel in create_selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=5000):
                        el.click()
                        print(f"[*] Clicked Create")
                        time.sleep(3)
                        break
                except:
                    continue

            # After creation, look for Download JSON button
            page.screenshot(path=screenshot_path.replace(".png", "_after_create.png"), full_page=True)

            download_selectors = [
                "text=Download JSON",
                "text=DOWNLOAD JSON",
                "button:has-text('Download')",
                "a:has-text('Download')",
            ]
            for sel in download_selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=5000):
                        # Set up download handler
                        with page.expect_download() as download_info:
                            el.click()
                        download = download_info.value
                        download.save_as(OUTPUT_FILE)
                        print(f"[*] Downloaded client secret to {OUTPUT_FILE}")

                        # Verify it's valid JSON
                        with open(OUTPUT_FILE) as f:
                            data = json.load(f)
                        print(f"[*] Client ID: {data.get('installed', {}).get('client_id', 'unknown')}")
                        print("[+] SUCCESS! OAuth client created and saved.")
                        break
                except:
                    continue
            else:
                print("[!] Could not find Download button. The form may need more input.")
                print("[*] Complete the process manually in the browser window.")
                input("Press Enter after you've downloaded the JSON file...")
                # Check if file was saved
                if os.path.exists(OUTPUT_FILE):
                    print(f"[+] Found {OUTPUT_FILE}")
                else:
                    print("[!] File not found. Please save manually.")

        else:
            print("[!] Did not reach the OAuth client creation page.")
            print("[*] You may need to sign in. Complete in the browser window.")
            input("Press Enter after signing in...")

        # Keep browser open for user if needed
        print("[*] Browser will close in 5 seconds...")
        time.sleep(5)
        browser.close()

    if os.path.exists(OUTPUT_FILE):
        print(f"\n[+] DONE! Client secret saved to: {OUTPUT_FILE}")
    else:
        print(f"\n[-] FAILED. Client secret was not created.")


if __name__ == "__main__":
    main()
