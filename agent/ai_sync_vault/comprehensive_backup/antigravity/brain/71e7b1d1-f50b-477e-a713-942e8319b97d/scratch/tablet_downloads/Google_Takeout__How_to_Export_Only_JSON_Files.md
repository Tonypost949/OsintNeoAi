# Google Takeout: How to Export Only JSON Files

Google Takeout does not currently offer a single button to switch all data to JSON format. By default, many services export in HTML or their native formats. To get **only** JSON files, you must configure the settings for each service and then filter the final download.

## 1. Manual Selection (The "Multiple Formats" Button)
For each service you want to export, follow these steps:
1.  Go to [Google Takeout](https://takeout.google.com/).
2.  Find the service (e.g., **My Activity**, **Google Play Store**, **Home**).
3.  Click the **Multiple formats** button next to the service name.
4.  In the pop-up, look for the dropdown menu (often under "Activity records" or "History").
5.  Change the format from **HTML** to **JSON**.
6.  Click **OK**.

> **Note:** For services like **Google Photos**, the JSON files are "sidecars" that contain metadata for your images. Google **does not** allow you to download these JSON files without the actual photos/videos. You will have to download the full archive and then extract only the JSONs.

## 2. Bulk Extracting Only JSON Files (Post-Download)
Since Google often forces you to download media or other files along with the JSONs, the fastest way to get **only** the JSON files after downloading and unzipping your archive is to use a simple command.

### On Windows (PowerShell):
Open PowerShell in your extracted Takeout folder and run:
```powershell
Get-ChildItem -Recurse -Filter *.json | Copy-Item -Destination "C:\Path\To\Your\JSON_Folder"
```

### On macOS / Linux (Terminal):
Open the terminal in your extracted Takeout folder and run:
```bash
find . -name "*.json" -exec cp {} /path/to/your/json_folder/ \;
```

## 3. Why are there "weird" JSON files?
When you download Google Photos, you will see files like `image.jpg.json`. These are not "new" images; they are metadata files created by Google to store information that isn't embedded in the image itself (like descriptions, GPS coordinates added later, or album info). If you only want the data, these are the files you need.

## Summary Table of JSON Availability
| Service | Can Export as JSON? | Default Format |
| :--- | :--- | :--- |
| **My Activity** | Yes (Manual Change) | HTML |
| **Location History** | Yes (Default) | JSON |
| **Google Photos** | Yes (Sidecars only) | Media + JSON |
| **Google Keep** | Yes (Default) | JSON |
| **Contacts** | Yes (Optional) | VCF / CSV / JSON |
| **Maps (Your places)** | Yes (Default) | JSON |
