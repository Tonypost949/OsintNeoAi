
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
# The URL to the Adobe Acrobat folder you want to download from.
# Make sure this is the specific page showing the files.
ADOBE_URL = "https://acrobat.adobe.com/documents/files"

# Path to your chromedriver executable.
# For simplicity, you can place chromedriver.exe in the same folder as this script
# and set CHROME_DRIVER_PATH = "chromedriver.exe"
# You must download the chromedriver version that matches YOUR Chrome browser version.
# Google "download chromedriver" to find it.
CHROME_DRIVER_PATH = "chromedriver.exe"

# The directory where you want to save the downloaded files.
# The script will create this directory if it doesn't exist.
DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), "adobe_downloads")
# --- END CONFIGURATION ---


def setup_driver():
    """Sets up the Chrome driver with specific options."""
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)

    chrome_options = webdriver.ChromeOptions()
    
    # Set the download directory for Chrome
    prefs = {
        "download.default_directory": DOWNLOAD_DIRECTORY,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # This should prevent opening PDFs in the browser
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def main():
    """Main function to run the download process."""
    driver = setup_driver()
    driver.get(ADOBE_URL)

    print("=" * 50)
    print("ACTION REQUIRED: Please log in to your Adobe account in the Chrome window.")
    print("After you have logged in and can see your files, press Enter here to continue.")
    print("=" * 50)
    input("Press Enter to continue after logging in...")

    # The script will now attempt to download the files.
    # We will need to add the logic for finding and clicking checkboxes and the download button.
    
    print("Login detected. Starting download process...")
    download_files(driver)


def download_files(driver):
    """
    Main logic to find and download files.
    
    IMPORTANT: You may need to update the CSS_SELECTORS below to match the
    HTML structure of the Adobe website. To do this:
    1. Right-click on the element you want to select (e.g., a file checkbox) in Chrome.
    2. Select "Inspect".
    3. In the developer tools, right-click on the highlighted HTML element.
    4. Go to "Copy" > "Copy selector".
    5. Paste the copied selector into the appropriate variable below.
    """
    # --- CSS SELECTORS (UPDATE THESE IF NEEDED) ---
    # Selector for the individual file items/rows in the list.
    FILE_ITEM_SELECTOR = "div.file-item-container" 
    # Selector for the checkbox within each file item.
    CHECKBOX_SELECTOR = "input[type='checkbox']"
    # Selector for the main download button that appears after selecting files.
    DOWNLOAD_BUTTON_SELECTOR = "button[data-testid='Download']"
    # Selector for the "Next Page" button if there is pagination.
    # If there is no "Next Page" button (e.g., infinite scroll), this needs to be adapted.
    NEXT_PAGE_SELECTOR = "button[data-testid='next-page']"
    # --- END CSS SELECTORS ---

    wait = WebDriverWait(driver, 10)

    while True:
        try:
            # Wait until file items are loaded
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, FILE_ITEM_SELECTOR)))
            
            # Find all file checkboxes on the current page
            all_checkboxes = driver.find_elements(By.CSS_SELECTOR, f"{FILE_ITEM_SELECTOR} {CHECKBOX_SELECTOR}")
            
            # Filter for only the checkboxes that haven't been processed yet (e.g., not disabled)
            # This logic might need to be more sophisticated depending on the site behavior
            visible_checkboxes = [cb for cb in all_checkboxes if cb.is_displayed()]

            if not visible_checkboxes:
                print("No more files found on this page.")
                break

            print(f"Found {len(visible_checkboxes)} files on this page.")
            
            # Process in batches of 50
            for i in range(0, len(visible_checkboxes), 50):
                batch = visible_checkboxes[i:i+50]
                
                print(f"Selecting a batch of {len(batch)} files...")
                for cb in batch:
                    # Scroll into view to make it clickable
                    driver.execute_script("arguments[0].scrollIntoView(true);", cb)
                    time.sleep(0.1) # small delay
                    cb.click()

                print("Clicking the download button...")
                download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, DOWNLOAD_BUTTON_SELECTOR)))
                download_button.click()

                # A simple wait for the download to start and process.
                # This is the most brittle part of the script. If downloads are large,
                # you might need to increase this time.
                print("Waiting for download to process... (adjust sleep time if needed)")
                time.sleep(30) 

                print("Deselecting files...")
                for cb in batch:
                    if cb.is_selected():
                        cb.click()
                time.sleep(2)

            # Check for a "Next Page" button
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, NEXT_PAGE_SELECTOR)
                if next_page_button.is_enabled():
                    print("Moving to the next page...")
                    next_page_button.click()
                else:
                    print("End of pages.")
                    break
            except Exception:
                print("No 'Next Page' button found. Assuming all files have been processed.")
                break
        
        except Exception as e:
            print(f"An error occurred: {e}")
            print("This might be because the CSS selectors are incorrect or the page structure has changed.")
            print("Please check the selectors in the script and try again.")
            break
 

    print("Script finished. Check the '{}' folder for your files.".format(DOWNLOAD_DIRECTORY))
    driver.quit()


if __name__ == "__main__":
    main()
