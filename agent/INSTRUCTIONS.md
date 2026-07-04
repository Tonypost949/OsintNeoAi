# Instructions for Downloading Your Adobe Files

This guide will walk you through using the `adobe_downloader.py` script to automatically download your files.

## Step 1: Install Python

If you do not have Python installed, download and install it from the official website.
- **Link:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- During installation, **make sure to check the box that says "Add Python to PATH"**.

## Step 2: Install Selenium

Once Python is installed, you need to install the `selenium` library. Open your command prompt (CMD or PowerShell) and run this command:

```
pip install selenium
```

## Step 3: Download ChromeDriver

Selenium uses a special driver to control your Chrome browser. You MUST download the version of ChromeDriver that **exactly matches** your version of Google Chrome.

1.  **Find your Chrome Version:**
    - Open Chrome, click the three dots (`...`) in the top-right corner.
    - Go to `Help` > `About Google Chrome`.
    - Note the version number (e.g., `108.0.5359.125`).

2.  **Download ChromeDriver:**
    - Go to the official ChromeDriver download page.
    - **Link:** [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
    - Find the version that matches your Chrome version and download the `chromedriver_win32.zip` file.

3.  **Place ChromeDriver:**
    - Unzip the downloaded file to get `chromedriver.exe`.
    - **IMPORTANT:** Move `chromedriver.exe` into the **same folder** as the `adobe_downloader.py` script.

## Step 4: Run the Script

1.  Navigate to the script's directory in your command prompt.
2.  Run the script with this command:

    ```
    python adobe_downloader.py
    ```

3.  A new Chrome window will open. **Log in to your Adobe account manually.**
4.  After you are logged in and can see your files, go back to the command prompt and press `Enter`.
5.  The script will then take over, selecting and downloading your files in batches.

## Troubleshooting

**"The script isn't clicking the right buttons!"**

If the script fails to find checkboxes or the download button, you need to update the CSS selectors in the `adobe_downloader.py` file.

1.  Open `adobe_downloader.py` in a text editor.
2.  Find the `--- CSS SELECTORS ---` section.
3.  Follow the instructions in the script's comments to get the correct selectors from your browser and paste them into the script.
    - Right-click on the element (e.g., a file checkbox).
    - Choose "Inspect".
    - In the new panel, right-click the highlighted code.
    - Choose `Copy` > `Copy selector`.
    - Paste it into the correct variable in the script and save the file.
4.  Run the script again.
